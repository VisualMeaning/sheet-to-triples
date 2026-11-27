# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the run.py module of sheet-to-triples."""

import io
import json
import os
import unittest

import rdflib

from pyfakefs import fake_filesystem_unittest
from unittest import mock

from .. import run, trans


def _mock_open(data):
    return mock.patch('builtins.open', mock.mock_open(read_data=data))


def _mock_basename():
    return mock.patch(
        'os.path.basename',
        side_effect=lambda x: '/basename/' + x,
    )


def _mock_xl_load_book():
    return mock.patch(
        'sheet_to_triples.xl.load_book',
        side_effect=lambda x: '/load_book/' + x,
    )


def _mock_xl_iter_sheet(test_iter):
    return mock.patch(
        'sheet_to_triples.xl.iter_sheet',
        return_value=test_iter
    )


class StubArgs:
    """Stub class with attribute values matching args keys."""
    def __init__(self, args):
        for arg in args:
            setattr(self, arg, args[arg])


class StubRunner:
    """Initialise a Runner with some stub values as defaults."""
    # used where default values are relatively unimportant - they can be
    # selectively overridden when calling get_runner if they are important

    def __init__(self):
        model = {
            'terms': [
                {'subj': 'test_subj', 'pred': 'test_pred', 'obj': 'test_obj'}
            ]
        }
        self.args = {
            'books': ['test_book1.xlsx'],
            'model': model,
            'purge_except': lambda x: True,
            'resolve_same': False,
            'use_ontology_normalisation': False,
            'drop_duplicates': 'keep-newest',
            'verbose': False,
            'non_unique': set(),
        }

    def get_runner(self, args={}):
        return run.Runner(**{**self.args, **args})


class RunnerTestCase(unittest.TestCase):

    def test_from_args(self):
        model = {
            'terms': [
                {'subj': 'test_subj', 'pred': 'test_pred', 'obj': 'test_obj'}
            ]
        }
        argvalues = {
            'book': ['test_book1.xlsx', 'test_book2.xlsx'],
            'model': 'model.json',
            'purge_except': lambda x: True,
            'resolve_same': False,
            'use_ontology_normalisation': False,
            'drop_duplicates': 'keep-newest',
            'verbose': False,
        }
        args = StubArgs(argvalues)
        model_data = json.dumps(model)

        with _mock_basename(), _mock_xl_load_book(), _mock_open(model_data):
            runner = run.Runner.from_args(args)
        expected_books = {
            '/basename/test_book1.xlsx': '/load_book/test_book1.xlsx',
            '/basename/test_book2.xlsx': '/load_book/test_book2.xlsx',
        }
        expected_attrs = [
            ('books', expected_books),
            ('model', model),
            ('normalisation_params', {
                'from_ontology': False,
                'resolve_same': False,
                'drop_duplicates': 'keep-newest',
                'non_uniques': run._default_non_unique
            }),
            ('verbose', False),
        ]
        for attr, expected in expected_attrs:
            with self.subTest(attr=attr):
                self.assertEqual(getattr(runner, attr), expected)

        self.assertIsInstance(runner.graph, rdflib.graph.Graph)
        # just check it's not empty, leave value checking to test_rdf
        self.assertTrue([n for n in runner.graph.subjects()])

    def test_from_args_no_book(self):
        argvalues = {
            'book': [],
            'model': 'model.json',
            'purge_except': lambda x: True,
            'resolve_same': False,
            'use_ontology_normalisation': False,
            'drop_duplicates': 'keep-newest',
            'verbose': False,
        }
        args = StubArgs(argvalues)
        model_data = json.dumps({'terms': []})
        with _mock_open(model_data):
            runner = run.Runner.from_args(args)

        self.assertEqual(runner.books, {})

    def test_from_args_default_model(self):
        argvalues = {
            'book': [],
            'model': run.default_model,
            'purge_except': lambda x: True,
            'resolve_same': False,
            'use_ontology_normalisation': False,
            'drop_duplicates': 'keep-newest',
            'verbose': False,
        }
        args = StubArgs(argvalues)
        runner = run.Runner.from_args(args)

        self.assertEqual(runner.model, {'terms': []})

    def test_for_ms_owner_file(self):
        argvalues = {
            'book': ['test.xlsx', '~$test.xlsx'],
            'model': run.default_model,
            'purge_except': lambda x: True,
            'resolve_same': False,
            'use_ontology_normalisation': False,
            'drop_duplicates': 'keep-newest',
            'verbose': False,
        }
        args = StubArgs(argvalues)
        with _mock_xl_load_book():
            runner = run.Runner.from_args(args)

        self.assertEqual(runner.books, {'test.xlsx': '/load_book/test.xlsx'})

    def test_from_args_no_model(self):
        argvalues = {
            'book': [],
            'model': None,
            'purge_except': lambda x: True,
            'resolve_same': False,
            'use_ontology_normalisation': False,
            'drop_duplicates': 'keep-newest',
            'verbose': False,
        }
        args = StubArgs(argvalues)
        runner = run.Runner.from_args(args)

        self.assertEqual(runner.model, None)

    def test_init_no_model(self):
        runner = StubRunner().get_runner(args={'model': None})
        self.assertIsInstance(runner.graph, rdflib.graph.Graph)
        self.assertFalse([n for n in runner.graph.subjects()])

    def test_use_non_uniques(self):
        transforms = [
            trans.Transform('test1', {'non_unique': ['http://a.test']}),
            trans.Transform('test2', {'non_unique': ['http://b.test']}),
        ]
        runner = StubRunner().get_runner()
        runner.use_non_uniques(transforms)
        self.assertEqual(
            runner.normalisation_params['non_uniques'],
            {'http://a.test', 'http://b.test'},
        )

    def test_run_model_changes(self):
        details = {
            'data': [
                {'col1': 'http://a.test', 'col2': '1'},
                {'col1': 'http://b.test', 'col2': '2'},
                {'col1': 'http://b.test', 'col2': '2'}
            ],
            'lets': {
                'iri': '{row[col1]}'
            },
            'triples': [
                ('{iri}', 'http://pred.test', '{row[col2]}'),
            ]
        }
        transform = trans.Transform('test', details)

        # overwrite default terms as we want to test them
        args = {
            'model': {
                'terms': [
                    {'subj': 'a', 'pred': 'b', 'obj': 'c'}
                ]
            }
        }
        runner = StubRunner().get_runner(args)

        runner.run([transform])

        # should have default value + derived rows from details
        # also should have duplicate row in details['data'] removed
        expected_terms = [
            {'subj': 'a', 'pred': 'b', 'obj': 'c'},
            {
                'subj': 'http://a.test',
                'pred': 'http://pred.test',
                'obj': '1',
            },
            {
                'subj': 'http://b.test',
                'pred': 'http://pred.test',
                'obj': '2',
            },
        ]
        self.assertEqual(runner.model, {'terms': expected_terms})

    def test_run_non_unique_updated(self):
        details = {
            'non_unique': ['http://pred']
        }
        transform = trans.Transform('test', details)
        # initialise with non-empty default non_unique list
        runner = StubRunner().get_runner({'non_unique': {'http://a.test'}})
        runner.run([transform])
        self.assertEqual(
            runner.normalisation_params['non_uniques'],
            {'http://a.test', 'http://pred'},
        )

    def _create_row_iter(self, rows):
        row_iter = []
        for row in rows:
            row_iter.append([StubArgs({'value': v}) for v in row])
        return row_iter

    def test_run_with_book(self):
        details = {
            'book': 'test_book1.xlsx',
            'sheet': 'test_sheet.xlsx',
            'triples': [
                (
                    'http://{row[col1]}.test',
                    'http://pred.test',
                    '{row[col2]}',
                ),
            ]
        }
        transform = trans.Transform('test', details)

        # fake book data for our mock iter_sheet function to return
        rows = [('col1', 'col2'), ('a', 'b'), ('', '')]
        row_iter = self._create_row_iter(rows)

        args = {
            'books': {
                'test_book1.xlsx': 'book object'
            },
            'model': {
                'terms': []
            }
        }
        runner = StubRunner().get_runner(args)

        with _mock_xl_iter_sheet(row_iter) as mis:
            runner.run([transform])

        expected_terms = [
            {
                'subj': 'http://a.test',
                'pred': 'http://pred.test',
                'obj': 'b',
            },
            {
                'subj': 'http://col1.test',
                'pred': 'http://pred.test',
                'obj': 'col2',
            },
        ]
        self.assertEqual(runner.model, {'terms': expected_terms})
        mis.assert_called_once_with(
            ['book object'], 'test_sheet.xlsx', 'utf-8')

    def test_run_with_sheet_but_no_book(self):
        details = {
            'sheet': 'test_sheet.xlsx',
            'triples': [
                (
                    'http://{row[col1]}.test',
                    'http://pred.test',
                    '{row[col2]}',
                ),
            ]
        }
        transform = trans.Transform('test', details)

        rows = [('col1', 'col2'), ('', '')]
        row_iter = self._create_row_iter(rows)

        args = {
            'books': {
                'test_book1.xlsx': 'book object1',
                'test_book2.xlsx': 'book object2',
            },
            'model': {
                'terms': []
            }
        }
        runner = StubRunner().get_runner(args)

        with _mock_xl_iter_sheet(row_iter) as mis:
            runner.run([transform])

        # should pass full list of book objects to iter_sheet
        mis.assert_called_once
        self.assertEqual(
            list(mis.call_args.args[0]),
            ['book object1', 'book object2'],
        )

    def test_run_error_if_no_matching_book(self):
        details = {
            'book': 'test_book2.xlsx',
            'sheet': 'test_sheet.xlsx',
        }
        transform = trans.Transform('test', details)

        rows = [('col1', 'col2'), ('', '')]
        row_iter = self._create_row_iter(rows)

        args = {
            'books': {
                'test_book1.xlsx': 'book object'
            },
        }
        runner = StubRunner().get_runner(args)
        with _mock_xl_iter_sheet(row_iter) as mis, \
                self.assertRaises(ValueError) as error:
            runner.run([transform])

        self.assertEqual(
            str(error.exception),
            'required book test_book2.xlsx not found'
        )

        mis.assert_not_called()

    def test_run_verbose(self):
        details = {
            'data': [{'col1': 'a', 'col2': 'b', 'col3': 'c'}],
            'triples': [
                (
                    'http://{row[col1]}.test',
                    'http://{row[col2]}.test',
                    '{row[col3]}'
                ),
            ]
        }
        transform = trans.Transform('test', details)
        args = {'verbose': True, 'books': {}}

        buffer = io.StringIO()
        with mock.patch('sys.stdout', new=buffer):
            runner = StubRunner().get_runner(args)
            runner.run([transform])

        self.assertEqual(
            buffer.getvalue(),
            ('# not retained 0 terms\n@prefix ns1: <http://> .\n\n'
             'ns1:a.test ns1:b.test "c" .\n\n\n')
        )

    def test_ns(self):
        runner = StubRunner().get_runner()
        self.assertIsInstance(runner.ns, rdflib.namespace.NamespaceManager)

    def test_load_model_full(self):
        with _mock_open('{"terms": []}') as mo:
            data = run.Runner.load_model('test.json')

        self.assertEqual(data, {'terms': []})
        mo.assert_called_once_with('test.json', 'rb')

    def test_load_model_terms(self):
        terms = [{'subj': 'a-subj', 'pred': 'a-pred', 'obj': 'a-obj'}]
        with _mock_open(json.dumps(terms)) as mo:
            data = run.Runner.load_model('test.json')

        self.assertEqual(data, {'terms': terms})
        mo.assert_called_once_with('test.json', 'rb')

    def test_load_model_invalid(self):
        with _mock_open('["some", "json"]') as mo:
            with self.assertRaises(ValueError):
                run.Runner.load_model('test.json')

        mo.assert_called_once_with('test.json', 'rb')

    def test_save_model(self):
        args = {
            'model': {
                'terms': [
                    {'subj': 'a', 'pred': 'b', 'obj': 'c'}
                ]
            }
        }
        runner = StubRunner().get_runner(args)
        with _mock_open('') as mo:
            runner.save_model('test.json')

        mo.assert_called_once_with('test.json', 'w')

        handle = mo()
        # json.dump writes in a way that is awkward to test - 19 separate
        # write calls for the single json term in the model. need to
        # splice them together to get something that's sane
        jsonstring = ''.join([c.args[0] for c in handle.write.mock_calls])
        expected = '{"terms": [{"subj": "a", "pred": "b", "obj": "c"}]}'
        self.assertEqual(jsonstring, expected)


def _ttl(*triples):
    return ''.join(f'<http://{s}.test> <http://{p}.test> "{o}" .\n'
                   for s, p, o in triples)


def _terms(*triples):
    return [
        {'subj': f'http://{s}.test', 'pred': f'http://{p}.test', 'obj': o}
        for s, p, o in triples
    ]


def _transform(name, *triples, **details):
    """Transform from fixed data giving triples in the same short form."""
    return trans.Transform(name, dict(details, data=[{}], triples=[
        (f'http://{s}.test', f'http://{p}.test', o) for s, p, o in triples
    ]))


class RunnerGraphsTestCase(fake_filesystem_unittest.TestCase):
    """Precedence between the model, added graphs and transform outputs."""

    def setUp(self):
        self.setUpPyfakefs()

    def _runner(self, terms=(), **args):
        args.setdefault('model', {'terms': list(terms)})
        with mock.patch('sys.stdout', new=io.StringIO()):
            return StubRunner().get_runner(args)

    def _run(self, runner, graphs=(), transforms=()):
        for path in graphs:
            runner.add_graph(path)
        with mock.patch('sys.stdout', new=io.StringIO()) as stdout:
            runner.run(transforms)
        return stdout.getvalue()

    def test_add_graph_cli_order_wins(self):
        # Lexical order of both paths and values disagrees with given order
        self.fs.create_file('b.ttl', contents=_ttl(('a', 'p', '1')))
        self.fs.create_file('a.ttl', contents=_ttl(('a', 'p', '2')))
        for order, expected in (
            (['b.ttl', 'a.ttl'], '2'),
            (['a.ttl', 'b.ttl'], '1'),
        ):
            with self.subTest(order=order):
                runner = self._runner()
                self._run(runner, order)
                self.assertEqual(
                    runner.model['terms'], _terms(('a', 'p', expected)))

    def test_add_graph_overrides_model(self):
        self.fs.create_file('g.ttl', contents=_ttl(('a', 'p', 'graph')))
        runner = self._runner(_terms(('a', 'p', 'model')))
        self._run(runner, ['g.ttl'])
        self.assertEqual(runner.model['terms'], _terms(('a', 'p', 'graph')))

    def test_transform_overrides_model_and_graphs(self):
        self.fs.create_file('g.ttl', contents=_ttl(
            ('a', 'p', 'graph'), ('b', 'p', 'graph')))
        runner = self._runner(_terms(('a', 'p', 'model'), ('c', 'p', 'model')))
        self._run(runner, ['g.ttl'], [
            _transform('t1', ('a', 'p', 'tf'), ('b', 'p', 'tf'))])
        self.assertEqual(runner.model['terms'], _terms(
            ('a', 'p', 'tf'), ('b', 'p', 'tf'), ('c', 'p', 'model')))

    def test_later_transform_overrides_earlier(self):
        runner = self._runner()
        self._run(runner, transforms=[
            _transform('t1', ('a', 'p', 'first')),
            _transform('t2', ('a', 'p', 'second')),
        ])
        self.assertEqual(runner.model['terms'], _terms(('a', 'p', 'second')))

    def test_keep_oldest_reverses(self):
        self.fs.create_file('g1.ttl', contents=_ttl(('a', 'p', 'g1')))
        self.fs.create_file('g2.ttl', contents=_ttl(
            ('a', 'p', 'g2'), ('b', 'p', 'g2')))
        runner = self._runner(
            _terms(('a', 'p', 'model')), drop_duplicates='keep-oldest')
        self._run(runner, ['g1.ttl', 'g2.ttl'], [
            _transform('t1', ('a', 'p', 'tf'), ('b', 'p', 'tf'))])
        self.assertEqual(runner.model['terms'], _terms(
            ('a', 'p', 'model'), ('b', 'p', 'g2')))

    def test_triple_in_several_graphs_once(self):
        graph_paths = ['first.ttl', 'second.ttl', 'repeat.ttl']
        graph_contents = (
            _ttl(('a', 'p', '1')), _ttl(('a', 'p', '2')), _ttl(('a', 'p', '1')),
        )
        for path, contents in zip(graph_paths, graph_contents):
            self.fs.create_file(path, contents=contents)
        runner = self._runner(_terms(('a', 'p', '1')), non_unique={'http://p.test'})
        self._run(runner, graph_paths, [_transform('t', ('a', 'p', '1'))])
        self.assertEqual(
            runner.model['terms'], _terms(('a', 'p', '1'), ('a', 'p', '2')))

    def test_self_conflict_warns_and_is_deterministic(self):
        lines = [('a', 'p', 'x'), ('a', 'p', 'y'), ('b', 'p', 'z')]
        self.fs.create_file('one.ttl', contents=_ttl(*lines))
        self.fs.create_file('two.ttl', contents=_ttl(*lines[::-1]))
        outputs = []
        for path in ('one.ttl', 'two.ttl'):
            runner = self._runner()
            stdout = self._run(runner, [path])
            self.assertIn(
                f'# warning: add-graph/1/{path} has several values for '
                '<http://a.test> <http://p.test>\n', stdout)
            self.assertIn('#   x\n', stdout)
            self.assertEqual(stdout.count(' (kept)\n'), 1)
            outputs.append(runner.model['terms'])
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(len(outputs[0]), 2)

    def test_dropped_names_graphs(self):
        self.fs.create_file('g.ttl', contents=_ttl(('a', 'p', 'new')))
        runner = self._runner(_terms(('a', 'p', 'old')), model_name='in.json')
        stdout = self._run(runner, ['g.ttl'])
        self.assertEqual(stdout, (
            '# dropped <http://a.test> <http://p.test> old\n'
            '#   from model/0/in.json, kept from add-graph/1/g.ttl: new\n'
        ))

    def test_dropped_same_serialisation_only_verbose(self):
        """Literal and IRI with the same text only differ to rdflib."""
        self.fs.create_file('g.ttl', contents=(
            '<http://a.test> <http://p.test> <http://o.test> .\n'))
        terms = [{'subj': 'http://a.test', 'pred': 'http://p.test',
                  'obj': 'http://o.test'}]
        for verbose, expect_lines in ((False, 0), (True, 2)):
            with self.subTest(verbose=verbose):
                runner = self._runner(list(terms), verbose=verbose)
                stdout = self._run(runner, ['g.ttl'])
                self.assertEqual(
                    stdout.count('\n'), expect_lines, stdout)
                self.assertEqual(runner.model['terms'], terms)

    def test_ontology_normalisation_reads_graphs(self):
        """With -n, functional properties can come from an added graph."""
        owl = 'http://www.w3.org/2002/07/owl#'
        rdf_type = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        self.fs.create_file('onto.ttl', contents=(
            f'<http://one.test> <{rdf_type}> <{owl}FunctionalProperty> .\n'))
        runner = self._runner(
            _terms(('a', 'one', 'old'), ('a', 'many', 'old')),
            use_ontology_normalisation=True)
        self._run(runner, ['onto.ttl'], [
            _transform('t', ('a', 'one', 'new'), ('a', 'many', 'new'))])
        self.assertEqual(
            [(t['pred'], t['obj']) for t in runner.model['terms']
             if t['subj'] == 'http://a.test'],
            [('http://many.test', 'new'), ('http://many.test', 'old'),
             ('http://one.test', 'new')])

    def test_resolve_same_after_merge_inputs(self):
        same_as = 'http://www.w3.org/2002/07/owl#sameAs'
        self.fs.create_file('g.ttl', contents=(
            f'<http://new.test> <{same_as}> <http://old.test> .\n'
            + _ttl(('new', 'p', 'graph'))))
        runner = self._runner(
            _terms(('old', 'p', 'model'), ('old', 'q', 'model')),
            resolve_same=True)
        self._run(runner, ['g.ttl'])
        self.assertEqual(runner.model['terms'], _terms(
            ('new', 'p', 'graph'), ('new', 'q', 'model')))

    def test_prefix_from_added_graph_usable(self):
        self.fs.create_file('g.ttl', contents=(
            '@prefix ex: <http://ex.test/> .\nex:a ex:p "1" .\n'))
        runner = self._runner()
        runner.add_graph('g.ttl')
        tf = trans.Transform('t', {'non_unique': ['ex:p']})
        self.assertEqual(tf.get_non_uniques(runner.ns), {'http://ex.test/p'})
        merged, _ = runner.merge()
        self.assertEqual(
            dict(merged.namespaces())['ex'], rdflib.URIRef('http://ex.test/'))

    def test_graph_identifiers(self):
        self.fs.create_file('dir/my graph.ttl', contents=_ttl(('a', 'p', '1')))
        runner = self._runner(model_name='in.json')
        runner.add_graph('dir/my graph.ttl')
        self._run(runner, transforms=[_transform('my/tf', ('a', 'p', '2'))])
        self.assertEqual(
            [run.graph_label(g.identifier) for g in runner.graphs],
            ['model/0/in.json', 'add-graph/1/dir/my graph.ttl',
             'transform/2/my/tf'])
        self.assertEqual(
            str(runner.graphs[1].identifier),
            'http://visual-meaning.com/rdf/graph/add-graph/1/dir/my%20graph.ttl')
        self.assertEqual(
            set(c.identifier for c in runner.dataset.graphs()),
            set(g.identifier for g in runner.graphs)
            | {runner.dataset.default_graph.identifier})

    def test_graph_identifier_path_names(self):
        tests = {
            'name': 'name',
            'dir/g.ttl': 'dir/g.ttl',
            './dir/../g.ttl': 'g.ttl',
            os.path.abspath(os.path.join('somewhere', 'g.ttl')): 'g.ttl',
            os.path.join(os.pardir, 'books', 'g.ttl'): 'g.ttl',
        }
        for name, expected in tests.items():
            with self.subTest(name=name):
                self.assertEqual(
                    run.graph_label(run.graph_identifier('add-graph', 3, name)),
                    'add-graph/3/' + expected)

    def test_no_model_names_graph_by_kind(self):
        runner = self._runner(model_name=None)
        self.assertEqual(
            run.graph_label(runner.graphs[0].identifier), 'model/0')
