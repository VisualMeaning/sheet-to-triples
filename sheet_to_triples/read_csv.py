# Copyright 2022 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Loading tabular data from csv files."""

import csv


class Cell:
    """Class wrapper for row value."""

    def __init__(self, value):
        self.value = value


class Book:
    """Wrapper around csv reader object to present common interface."""

    def __init__(self, path):
        self._path = path

    def __repr__(self):
        return f'{self.__class__.__name__}({self._path})'

    @classmethod
    def from_path(cls, path):
        return cls(path)

    def iter_rows_in_sheet(self, sheet, sheet_encoding):
        with open(self._path, 'r', encoding=sheet_encoding) as csv_file:
            try:
                for index, row in enumerate(csv.reader(csv_file)):
                    yield [Cell(v) for v in row]
            except UnicodeDecodeError:
                raise ValueError(f'Invalid encoding on row number {index}')
