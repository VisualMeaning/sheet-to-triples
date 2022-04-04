# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the run.py module of sheet-to-triples."""

import io
import json
import unittest

import rdflib

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
            'verbose': False,
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
            ('non_unique', set()),
            ('resolve_same', False),
            ('verbose', False)
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
            'verbose': False,
        }
        args = StubArgs(argvalues)
        runner = run.Runner.from_args(args)

        self.assertEqual(runner.model, {'terms': []})

    def test_from_args_no_model(self):
        argvalues = {
            'book': [],
            'model': None,
            'purge_except': lambda x: True,
            'resolve_same': False,
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
            runner.non_unique,
            {'http://a.test', 'http://b.test'},
        )

    def test_set_terms(self):
        triples = [('new_test_subj', 'new_test_pred', 'new_test_obj')]
        runner = StubRunner().get_runner()
        runner.set_terms(triples)

        expected = [
            {
                    'subj': 'new_test_subj',
                    'pred': 'new_test_pred',
                    'obj': 'new_test_obj',
            }
        ]
        self.assertEqual(runner.model['terms'], expected)

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
        runner = StubRunner().get_runner()
        runner.run([transform])
        self.assertEqual(runner.non_unique, {'http://pred'})

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
        mis.assert_called_once_with(['book object'], 'test_sheet.xlsx')

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

    def test_load_model(self):
        with _mock_open('["some", "json"]') as mo:
            data = run.Runner.load_model('test.json')

        self.assertEqual(data, ['some', 'json'])
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
