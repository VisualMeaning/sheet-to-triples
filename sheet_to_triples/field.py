# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Interfaces for mapping from tabular data."""

import ast
import functools
import json
import re

import pycountry

_TYPES = {
    'pain': 'vm:Painpoint',
    'brig': 'vm:Brightspot',
}


_CAPTYPES = {
    'socia': 'vm:capitalTypes/social',
    'share': 'vm:capitalTypes/sharedFinancial',
    'finan': 'vm:capitalTypes/sharedFinancial',
    'human': 'vm:capitalTypes/human',
    'natur': 'vm:capitalTypes/environmental',
    'envir': 'vm:capitalTypes/environmental',
}


_CAPEFFECTS = {
    'vm:Painpoint': 'vm:harmsCapitalType',
    'vm:Brightspot': 'vm:aidsCapitalType',
}

_RAGCATEGORIES = {
    'Red': 'vm:_judged-negative',
    'Amber': 'vm:_judged-neutral',
    'Green': 'vm:_judged-positive',
}


def _must(value, exception_type=ValueError):
    """Raise exception_type if value is falsey."""
    if not value:
        raise exception_type('false value')
    return value


def _str(value):
    """Cast to string but raise if None or empty after strip."""
    if value is not None:
        if not isinstance(value, str):
            value = str(value)
        value = value.strip()
    if not value:
        raise ValueError('empty string value')
    return value


def _literal(value):
    """Treat as data serialised to a string."""
    if value is not None:
        if isinstance(value, str):
            return ast.literal_eval(value.strip())
    raise ValueError('not a data field')


@functools.lru_cache(maxsize=None)
def _resolve_country(name):
    return pycountry.countries.search_fuzzy(name)[0]


class Cell:
    """Single field value for interpretation in context."""

    _pattern = re.compile(r'\W+')

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return f'{self.__class__.__name__}({self._value!r})'

    def __str__(self):
        return _str(self._value)

    @property
    def as_slug(self):
        content = _str(self._value).replace('&', ' and ')
        return _must(self._pattern.sub('-', content).strip('-').lower())

    @property
    def as_uc(self):
        return _must(self._pattern.sub('', _str(self._value).title()))

    @property
    def as_json(self):
        return json.dumps(
            _must(self._value), ensure_ascii=False, separators=(',', ':'))

    @property
    def as_text(self):
        return _str(self._value)

    @property
    def as_capital(self):
        return _must(_CAPTYPES.get(_str(self._value)[:5].lower()), TypeError)

    @property
    def as_capital_effect(self):
        return _must(_CAPEFFECTS.get(self.as_type))

    @property
    def as_rag_category(self):
        return _must(_RAGCATEGORIES.get(self._value))

    @property
    def as_type(self):
        return _must(_TYPES.get(_str(self._value)[:4].lower()), TypeError)

    @property
    def as_type_slug(self):
        return self.as_type[3:].lower()

    @property
    def as_geo(self):
        try:
            lat, lng = map(float, _literal(self._value))
        except (SyntaxError, TypeError, ValueError):
            raise ValueError('not a geo field')
        return f'[{lat}, {lng}]'

    @property
    def as_date(self):
        return self._value.strftime('%Y-%m-%d')

    @property
    def as_date_or_text(self):
        try:
            return self.as_date
        except AttributeError:
            return self.as_text

    @property
    def as_country_code(self):
        return _resolve_country(_str(self._value)).alpha_2.lower()

    @property
    def must_exist(self):
        v = self._value
        if _str(v) if isinstance(v, str) else _must(v):
            return ''

    @property
    def exists(self):
        # Note, a whitespace-only string does exist, may be confusing!
        return bool(self._value)

    @property
    def not_exists(self):
        return not self.exists


class Row:
    """Group of fields keyed by name."""

    def __init__(self, fields):
        self.fields = fields

    def __repr__(self):
        return f'{self.__class__.__name__}({self.fields!r})'

    def __getitem__(self, key):
        return Cell(self.fields[key])

    def __setitem__(self, key, value):
        self.fields[key] = value

    def __contains__(self, item):
        return item in self.fields

    def __eq__(self, other):
        return self.fields == other.fields

    def col_exists(self, col):
        # check if a column exists with a value that isn't None
        return self.fields.get(col) is not None

    def cols_disjoint(self, cols):
        exists_cols = {k for k, v in self.fields.items() if v is not None}
        return exists_cols.isdisjoint(cols)

    def melt(self, melt_cols):
        self.fields['_has_melt'] = not self.cols_disjoint(melt_cols)
        for col in melt_cols:
            melted_row = Row(dict(self.fields))
            if melted_row.col_exists(col):
                melted_row['_melt_colname'] = col
                melted_row['_melt_value'] = str(melted_row[col])
            yield melted_row
