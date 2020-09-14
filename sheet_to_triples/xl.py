# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Loading tabular data from local spreadsheet files."""

import xlrd

from . import (
    field,
)


def load(filepath):
    return xlrd.open_workbook(filepath)


def find_sheet(books, sheet_name):
    for book in books:
        for sheet in book.sheets():
            if sheet.name == sheet_name:
                return sheet
    raise ValueError(f'sheet {sheet_name!r} not found')


def as_rows(sheet, required_headers):
    row_iter = sheet.get_rows()
    header_values = advance_headers(row_iter, required_headers)
    n_from_h = {h: i for i, h in enumerate(header_values)}
    for row in row_iter:
        yield field.Row({h: row[n_from_h[h]].value for h in required_headers})


def advance_headers(row_iter, required_headers):
    for row in row_iter:
        values = [cell.value for cell in row]
        if required_headers.issubset(values):
            return values
    raise ValueError('required headers not found')
