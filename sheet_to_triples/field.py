# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Interfaces for mapping from tabular data."""

import ast
import json
import re


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
        content = _str(self._value).replace('&', 'and')
        return _must(self._pattern.sub('-', content).lower())

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
    def as_type(self):
        return _must(_TYPES.get(_str(self._value)[:4].lower()), TypeError)

    @property
    def as_type_prefix(self):
        return self.as_type.lower() + '-'

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


class Row:
    """Group of fields keyed by name."""

    def __init__(self, fields):
        self._fields = fields

    def __repr__(self):
        return f'{self.__class__.__name__}({self._fields!r})'

    def __getitem__(self, key):
        return Cell(self._fields[key])
