# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the __main__ module of sheet-to-triples."""

import io
import json
import os

from pyfakefs import fake_filesystem_unittest
from unittest import mock

from .. import __main__ as main, run


class StubTransform:

    def __init__(self, name):
        self.name = name
        self.triples = []

    def uses_sheet(self):
        if 'book' in self.name:
            return True
        return False

    @classmethod
    def iter_from_name(cls, name, base_path=''):
        return [cls(os.path.join(base_path, name) + '.py')]


def _mock_stderr(io_class=io.StringIO):
    return mock.patch('sys.stderr', new_callable=io_class)


_iter_from_name = 'sheet_to_triples.trans.Transform'


@mock.patch(_iter_from_name, new=StubTransform('dummy'))
class TestParseArgs(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def test_parse_args_default(self):
        argv = ['dummy', 'transform1']
        args = main.parse_args(argv)
        defaults = [
            ('book', None),
            ('add_graph', None),
            ('model', None),
            ('model_out', None),
            ('resolve_same', True),
            ('debug', False),
            ('verbose', False),
            ('from_list', None),
            ('non_unique_from', None),
        ]

        for arg, expected in defaults:
            with self.subTest(arg=arg):
                self.assertEqual(getattr(args, arg), expected)

    def test_parse_args_transform(self):
        argv = ['dummy', 'transform1', 'transform2']
        args = main.parse_args(argv)

        self.assertEqual(
            [t.name for t in args.transform],
            ['transform1.py', 'transform2.py']
        )

    def test_parse_args_transform_error_if_requires_book(self):
        argv = ['dummy', 'booktransform1']

        # this makes any unexpected lower level exceptions harder to debug
        # TODO: come up with a nicer way of suppressing "normal" error output
        with _mock_stderr() as stderr, self.assertRaises(SystemExit) as e:
            main.parse_args(argv)

        self.assertEqual(e.exception.code, 2)

        # argparse spits out usage info so need to isolate error message
        message = stderr.getvalue().strip().splitlines()[-1]
        self.assertEqual(
            message,
            'dummy: error: transforms {\'booktransform1.py\'} require --book'
        )

    def test_parse_args_book_is_book(self):
        self.fs.create_file('book.xlsx')
        self.fs.create_file('book.xls')
        argv = [
            'dummy', 'transform1',
            '--book', 'book.xlsx',
            '--book', 'book.xls',
        ]
        args = main.parse_args(argv)

        expected = ['book.xlsx', 'book.xls']
        self.assertEqual(args.book, expected)

    def test_parse_args_book_is_dir(self):
        self.fs.create_file('rootdir1/book.xlsx')
        self.fs.create_file('rootdir1/book.xls')
        self.fs.create_file('rootdir1/notabook')
        argv = [
            'dummy', 'transform1',
            '--book', 'rootdir1'
        ]

        args = main.parse_args(argv)

        expected = [
            os.path.normpath('rootdir1/book.xlsx'),
            os.path.normpath('rootdir1/book.xls'),
        ]
        self.assertEqual(args.book, expected)

    def test_parse_args_from_list(self):
        self.fs.create_file('listpath.txt', contents=(
            'testdir/listtrans\ntestdir/listtrans2'))
        argv = ['dummy', 'transform1', '--from-list', 'listpath.txt']

        args = main.parse_args(argv)

        expected = [
            'transform1.py',
            os.path.normpath('testdir/listtrans.py'),
            os.path.normpath('testdir/listtrans2.py'),
        ]
        self.assertEqual(
            [t.name for t in args.transform],
            expected
        )

    def test_parse_args_non_unique_from(self):
        self.fs.create_file('listpath.txt', contents='listtrans\nlisttrans2')
        argv = ['dummy', 'transform1', '--non-unique-from', 'listpath.txt']

        args = main.parse_args(argv)

        self.assertEqual(
            [t.name for t in args.transform],
            ['transform1.py']
        )

        self.assertEqual(
            [nu.name for nu in args.non_unique_from],
            ['listtrans.py', 'listtrans2.py']
        )

    def test_parse_args_model_out_but_no_model(self):
        argv = ['dummy', 'transform1', '--model-out', 'output.json']
        args = main.parse_args(argv)
        self.assertEqual(args.model, run.default_model)

    def test_parse_args_bad_purge_except(self):
        argv = ['dummy', 'transform1', '--purge-except', 'bogus']

        # TODO: come up with a nicer way of suppressing "normal" error output
        with _mock_stderr() as stderr, self.assertRaises(SystemExit) as e:
            main.parse_args(argv)

        self.assertEqual(e.exception.code, 2)

        message = stderr.getvalue().strip().splitlines()[-1]
        self.assertEqual(
            message,
            'dummy: error: --purge-except must be one of none|geo|issues'
        )


# need to be able to pass in transform-specific data here, which means can't
# rely on above StubTransform because of classmethod in iter_from_name
class StubSingleTransform(StubTransform):

    def __init__(self, name, triples=[], non_uniques=[]):
        self.name = name
        self.triples = triples
        self.non_uniques = non_uniques

    def process(self, graph, row_iter):
        return self.triples

    def get_non_uniques(self, ns):
        return self.non_uniques

    def iter_from_name(self, name, base_path=''):
        return [self]


class TestMain(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def test_main_run_transform_save_model(self):
        argv = ['dummy', 'transform1', '--model-out', 'new.json']
        triples = [('a', 'b', 'c')]
        transform = StubSingleTransform('transform1', triples=triples)

        with mock.patch(_iter_from_name, new=transform):
            main.main(argv)

        # it should run tf.process(), add the triples to the runner model and
        # write to the buffer in our mock open object
        jsonstring = self.fs.get_object('new.json').contents
        expected = '{"terms": [{"subj": "a", "pred": "b", "obj": "c"}]}'
        self.assertEqual(jsonstring, expected)

    def test_main_run_transform_verbose(self):
        argv = ['dummy', '--model', 'test-in.json', '--verbose']
        model = {
            'terms': [
                {'subj': 'http://a.test', 'pred': 'http://b.test', 'obj': 'c'}
            ]
        }
        self.fs.create_file('test-in.json', contents=json.dumps(model))

        with mock.patch('sys.stdout', new_callable=io.StringIO) as stdout:
            main.main(argv)

        self.assertEqual(
            stdout.getvalue(),
            '# not retained 0 terms\n'
            '@prefix ns1: <http://> .\n\n'
            'ns1:a.test ns1:b.test "c" .\n\n\n'
        )

    def test_main_add_graph_verbose(self):
        """Adding a graph should update the model and normalise after."""
        argv = [
            'dummy', '--model', 'in.json', '--add-graph', 'bits.ttl',
            '--model-out', 'new.json', '-v'
        ]
        model = {
            'terms': [
                {'subj': 'http://a.test', 'pred': 'http://b.test', 'obj': 'c'}
            ]
        }
        self.fs.create_file('in.json', contents=json.dumps(model))
        self.fs.create_file('bits.ttl', contents=(
            '<http://a.test> <http://b.test> "b" .\n'))

        with mock.patch('sys.stdout', new_callable=io.StringIO) as stdout:
            main.main(argv)

        new_model = json.loads(self.fs.get_object('new.json').contents)
        self.assertEqual(model, new_model)
        self.assertEqual(
            '# not retained 0 terms\n'
            '# dropping <http://a.test> <http://b.test> b\n',
            stdout.getvalue())

    def test_run_runner_non_unique_from(self):
        argv = ['dummy', '--non-unique-from', 'list.txt']
        non_uniques = {'col1', 'col2'}
        transform = StubSingleTransform('transform1', non_uniques=non_uniques)
        self.fs.create_file('list.txt', contents='transform1')

        with mock.patch(_iter_from_name, new=transform):
            args = main.parse_args(argv)

        runner = run.Runner.from_args(args)
        main.run_runner(runner, args)

        self.assertEqual(runner.non_unique, non_uniques)
