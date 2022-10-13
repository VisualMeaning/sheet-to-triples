# Copyright 2020-2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Reading of old-format Excel files."""

import xlrd


class Book:
    """Wrapper around xlrd.book.Book to present common interface."""

    def __init__(self, book):
        self._book = book

    def __repr__(self):
        return f'{self.__class__.__name__}({self._book})'

    @classmethod
    def from_path(cls, path):
        return cls(xlrd.open_workbook(path))

    def iter_rows_in_sheet(self, sheet, *args):
        if sheet not in self._book.sheet_names():
            raise KeyError(sheet)
        return self._book.sheet_by_name(sheet).get_rows()
