# Copyright 2022 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Loading tabular data from csv files."""

import csv


class Cell:
    """Class wrapper for row value."""

    def __init__(self, value):
        self.value = value

    def value(self):
        return self.value

class Book:
    """Wrapper around csv reader object to present common interface."""

    def __init__(self, book):
        self._book = book

    def __repr__(self):
        return f'{self.__class__.__name__}({self._book})'

    @classmethod
    def from_path(cls, path):
        csv_file = open(path, 'r')
        return cls(csv.reader(csv_file))

    def iter_rows_in_sheet(self, sheet):
        try:
            for row in self._book:
                yield [Cell(v) for v in row]
        except UnicodeDecodeError:
            raise ValueError(f'Invalid encoding on row {row[0]}')
