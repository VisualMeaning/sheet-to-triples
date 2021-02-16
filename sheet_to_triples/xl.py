# Copyright 2020-2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Loading tabular data from local spreadsheet files."""

from . import (
    field,
)


def load_book(filepath):
    ext = filepath.rsplit('.', 1)[-1].lower()
    if ext == 'xls':
        from .xls import Book
    elif ext == 'xlsx':
        from .xlsx import Book
    else:
        raise ValueError(f'unsupported format: .{ext}')
    return Book.from_path(filepath)


def iter_sheet(books, sheet_name):
    last_err = None
    for book in books:
        try:
            return book.iter_rows_in_sheet(sheet_name)
        except KeyError as e:
            last_err = e
    raise ValueError(f'sheet {sheet_name!r} not found') from last_err


def as_rows(row_iter, required_headers):
    header_values = advance_headers(row_iter, required_headers)
    n_from_h = {h: i for i, h in reversed(list(enumerate(header_values)))}
    for row in row_iter:
        if all(not r.value for r in row):
            return
        yield field.Row({h: row[n_from_h[h]].value for h in required_headers})


def advance_headers(row_iter, required_headers):
    for row in row_iter:
        values = [cell.value for cell in row]
        if required_headers.issubset(values):
            return values
    raise ValueError('required headers not found')
