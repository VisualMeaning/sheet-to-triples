# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the __main__ module of sheet-to-triples."""

import io
import json
import os
import unittest

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


def _mock_os_path_walk(walk_data):
    return mock.patch('os.walk', return_value=walk_data)


def _mock_os_path_dirname(dirname):
    return mock.patch('os.path.dirname', return_value=dirname)


def _mock_os_path_isdir(isdir):
    return mock.patch('os.path.isdir', return_value=isdir)


def _mock_open(data):
    return mock.patch('builtins.open', mock.mock_open(read_data=data))


def _mock_stderr(buffer):
    return mock.patch('sys.stderr', new=buffer)


_iter_from_name = 'sheet_to_triples.trans.Transform'


@mock.patch(_iter_from_name, new=StubTransform('dummy'))
class TestParseArgs(unittest.TestCase):

    def test_parse_args_default(self):
        argv = ['dummy', 'transform1']
        args = main.parse_args(argv)
        defaults = [
            ('book', None),
            ('add_graph', None),
            ('model', None),
            ('model_out', 'new.json'),
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
        buffer = io.StringIO()

        # this makes any unexpected lower level exceptions harder to debug
        # TODO: come up with a nicer way of suppressing "normal" error output
        with _mock_stderr(buffer), self.assertRaises(SystemExit) as e:
            main.parse_args(argv)

        self.assertEqual(e.exception.code, 2)

        # argparse spits out usage info so need to isolate error message
        message = buffer.getvalue().strip().splitlines()[-1]
        self.assertEqual(
            message,
            'dummy: error: transforms {\'booktransform1.py\'} require --book'
        )

    def test_parse_args_book_is_book(self):
        argv = [
            'dummy', 'transform1',
            '--book', 'book.xlsx',
            '--book', 'book.xls',
        ]

        with _mock_os_path_isdir(False) as isdir:
            args = main.parse_args(argv)

        expected = ['book.xlsx', 'book.xls']
        self.assertEqual([b for b in args.book], expected)

        self.assertEqual(
            [c.args[0] for c in isdir.call_args_list],
            expected
        )

    def test_parse_args_book_is_dir(self):
        argv = [
            'dummy', 'transform1',
            '--book', 'rootdir1'
        ]
        walk_data = [
            ('rootdir1', '_', ('book.xlsx', 'notabook', 'book.xls')),
        ]

        with _mock_os_path_isdir(True) as isdir, \
                _mock_os_path_walk(walk_data):
            args = main.parse_args(argv)

        expected = ['rootdir1/book.xlsx', 'rootdir1/book.xls']
        self.assertEqual([b for b in args.book], expected)

        isdir.assert_called_once_with('rootdir1')

    def test_parse_args_from_list(self):
        data = 'listtrans\nlisttrans2'
        argv = ['dummy', 'transform1', '--from-list', 'listpath.txt']

        with _mock_os_path_dirname('testdir'), \
                _mock_open(data) as mo:
            args = main.parse_args(argv)

        expected = [
            'transform1.py',
            'testdir/listtrans.py',
            'testdir/listtrans2.py',
        ]
        self.assertEqual(
            [t.name for t in args.transform],
            expected
        )

        mo.assert_called_once_with('listpath.txt', 'r')

    def test_parse_args_non_unique_from(self):
        data = 'listtrans\nlisttrans2'
        argv = ['dummy', 'transform1', '--non-unique-from', 'listpath.txt']

        with _mock_os_path_dirname(''), \
                _mock_open(data) as mo:
            args = main.parse_args(argv)

        self.assertEqual(
            [t.name for t in args.transform],
            ['transform1.py']
        )

        self.assertEqual(
            [nu.name for nu in args.non_unique_from],
            ['listtrans.py', 'listtrans2.py']
        )

        mo.assert_called_once_with('listpath.txt', 'r')

    def test_parse_args_bad_purge_except(self):
        argv = ['dummy', 'transform1', '--purge-except', 'bogus']
        buffer = io.StringIO()

        # TODO: come up with a nicer way of suppressing "normal" error output
        with _mock_stderr(buffer), \
                self.assertRaises(SystemExit) as e:
            main.parse_args(argv)

        self.assertEqual(e.exception.code, 2)

        message = buffer.getvalue().strip().splitlines()[-1]
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


class TestMain(unittest.TestCase):

    def test_main_run_transform_save_model(self):
        argv = ['dummy', 'transform1', '--model', 'test-in.json']
        triples = [('a', 'b', 'c')]
        transform = StubSingleTransform('transform1', triples=triples)

        with mock.patch(_iter_from_name, new=transform), \
                _mock_open('{"terms": []}') as mo:
            main.main(argv)

        # it should run tf.process(), add the triples to the runner model and
        # write to the buffer in our mock open object
        handle = mo()
        jsonstring = ''.join([c.args[0] for c in handle.write.mock_calls])
        expected = '{"terms": [{"subj": "a", "pred": "b", "obj": "c"}]}'
        self.assertEqual(jsonstring, expected)

    def test_main_run_transform_verbose(self):
        argv = ['dummy', '--model', 'test-in.json', '--verbose']
        model = {
            'terms': [
                {'subj': 'http://a.test', 'pred': 'http://b.test', 'obj': 'c'}
            ]
        }
        transform = StubSingleTransform('transform1')
        buffer = io.StringIO()

        with mock.patch(_iter_from_name, new=transform), \
                mock.patch('sys.stdout', new=buffer), \
                _mock_open(json.dumps(model)):
            main.main(argv)

        self.assertEqual(
            buffer.getvalue(),
            ('# dropped 0 terms\n@prefix ns1: <http://> .\n\n'
             'ns1:a.test ns1:b.test "c" .\n\n\n')
        )

    def test_run_runner_non_unique_from(self):
        argv = ['dummy', '--non-unique-from', 'transform2']
        non_uniques = {'col1', 'col2'}
        transform = StubSingleTransform('transform1', non_uniques=non_uniques)

        with mock.patch(_iter_from_name, new=transform), \
                _mock_open('dummy'),  _mock_os_path_dirname(''):
            args = main.parse_args(argv)
            runner = run.Runner.from_args(args)
            main.run_runner(runner, args)

        self.assertEqual(runner.non_unique, non_uniques)
