# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the xl, xls and xlsx modules of sheet-to-triples."""

import unittest

from unittest import mock

from .. import xl, xlsx, xls


class StubSheet:

    def __init__(self, name):
        self.name = name

    def _get_rows(self, caller):
        return 'test {} {}'.format(caller, self.name)

    def iter_rows(self):
        return self._get_rows('iter_rows')

    def get_rows(self):
        return self._get_rows('get_rows')


class StubXlsBook:

    def __init__(self, sheets):
        self.sheets = sheets

    def sheet_names(self):
        return self.sheets

    def sheet_by_name(self, sheet):
        return StubSheet(sheet)


class StubCell:

    def __init__(self, value):
        self.value = value


class TestXL(unittest.TestCase):

    _mock_xls_open = mock.patch(
            'xlrd.open_workbook', return_value='xls_book')

    _mock_xlsx_open = mock.patch(
            'openpyxl.load_workbook', return_value='xlsx_book')

    def test_load_book_xls(self):
        with self._mock_xls_open as xls_o:
            book = xl.load_book('testbook.xls')

        self.assertIsInstance(book, xls.Book)
        self.assertEqual(book._book, 'xls_book')
        xls_o.assert_called_with('testbook.xls')

    def test_load_book_xlsx(self):
        with self._mock_xlsx_open as xlsx_o:
            book = xl.load_book('testbook.xlsx')

        self.assertIsInstance(book, xlsx.Book)
        self.assertEqual(book._book, 'xlsx_book')
        xlsx_o.assert_called_with('testbook.xlsx', data_only=True)

    def test_load_book_not_excel_filetype(self):
        with self.assertRaises(ValueError) as error:
            xl.load_book('testbook.bogus')

        self.assertEqual(
            str(error.exception),
            'unsupported format: .bogus'
        )

    def test_iter_sheet_xlsx(self):
        books = [
            {'a': StubSheet('a')},
            {'b': StubSheet('b')},
        ]
        xslx_books = [xlsx.Book(book) for book in books]
        value = xl.iter_sheet(xslx_books, 'b')
        self.assertEqual(value, 'test iter_rows b')

    def test_iter_sheet_xlsx_no_matching_sheet(self):
        books = [
            {'a': StubSheet('a')},
            {'b': StubSheet('b')},
        ]
        xlsx_books = [xlsx.Book(book) for book in books]
        with self.assertRaises(ValueError) as error:
            xl.iter_sheet(xlsx_books, 'c')

        self.assertEqual(
            str(error.exception),
            "sheet 'c' not found"
        )

    def test_iter_sheet_xls(self):
        books = [
            StubXlsBook(['a']),
            StubXlsBook(['b']),
        ]
        xls_books = [xls.Book(book) for book in books]
        value = xl.iter_sheet(xls_books, 'b')
        self.assertEqual(value, 'test get_rows b')

    def test_iter_sheet_xls_no_matching_sheet(self):
        books = [
            StubXlsBook(['a']),
            StubXlsBook(['b']),
        ]
        xls_books = [xls.Book(book) for book in books]
        with self.assertRaises(ValueError) as error:
            xl.iter_sheet(xls_books, 'c')

        self.assertEqual(
            str(error.exception),
            "sheet 'c' not found"
        )

    @staticmethod
    def _convert_to_cells(row):
        return [StubCell(v) for v in row]

    def test_as_rows_skip_empty_false(self):
        row_iter = [
            ('col1', 'col2'),
            ('a', 'b'),
            ('', ''),
            ('c', 'd')
        ]
        cell_iter = [self._convert_to_cells(r) for r in row_iter]
        rows = xl.as_rows(cell_iter, {'col1', 'col2'}, False)
        expected = [
            {'col1': 'col1', 'col2': 'col2'},
            {'col1': 'a', 'col2': 'b'},
        ]
        self.assertEqual([r.fields for r in rows], expected)

    def test_as_rows_skip_empty_true(self):
        row_iter = [
            ('col1', 'col2'),
            ('a', 'b'),
            ('', ''),
            ('c', 'd')
        ]
        cell_iter = [self._convert_to_cells(r) for r in row_iter]
        rows = xl.as_rows(cell_iter, {'col1', 'col2'}, True)
        expected = [
            {'col1': 'col1', 'col2': 'col2'},
            {'col1': 'a', 'col2': 'b'},
            {'col1': 'c', 'col2': 'd'},
        ]
        self.assertEqual([r.fields for r in rows], expected)

    def test_advance_headers(self):
        row_iter = [
            ('a', 'b'),
            ('col1', 'col2'),
        ]
        cell_iter = [self._convert_to_cells(r) for r in row_iter]
        headers = xl.advance_headers(cell_iter, {'col1'})
        self.assertEqual(headers, ['col1', 'col2'])

    def test_advance_headers_no_match(self):
        row_iter = [
            ('a', 'b'),
            ('col1', 'col2'),
        ]
        cell_iter = [self._convert_to_cells(r) for r in row_iter]
        with self.assertRaises(ValueError) as error:
            xl.advance_headers(cell_iter, {'col2', 'col3', 'col4'})

        # also test message as there's a chunk of code that finds missing
        # columns that are then surfaced via the exception message
        self.assertEqual(
            str(error.exception),
            'required headers not found: col3, col4'
        )
