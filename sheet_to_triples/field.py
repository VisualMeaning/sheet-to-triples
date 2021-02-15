# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Interfaces for mapping from tabular data."""

import ast
import re


_TYPES = {
    'pain': 'vm:Painpoint',
    'brig': 'vm:Brightspot',
}


_CAPTYPES = {
    'socia': 'vm:capitalTypes/social',
    'finan': 'vm:capitalTypes/sharedFinancial',
    'human': 'vm:capitalTypes/human',
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


class Cell:
    """Single field value for interpretation in context."""

    _pattern = re.compile(r'\W+')

    def __init__(self, value):
        self._value = '' if value is None else value

    def __repr__(self):
        return f'{self.__class__.__name__}({self._value!r})'

    def __str__(self):
        return self._value

    @property
    def as_slug(self):
        content = self._value.replace('&', 'and').strip()
        return _must(self._pattern.sub('-', content).lower())

    @property
    def as_uc(self):
        return _must(self._pattern.sub('', self._value.strip().title()))

    @property
    def as_text(self):
        return _must(self._value.strip())

    @property
    def as_capital(self):
        return _must(_CAPTYPES.get(self._value.strip()[:5].lower()), TypeError)

    @property
    def as_capital_effect(self):
        return _must(_CAPEFFECTS.get(self.as_type))

    @property
    def as_type(self):
        return _must(_TYPES.get(self._value.strip()[:4].lower()), TypeError)

    @property
    def as_type_prefix(self):
        return self.as_type.lower() + '-'

    @property
    def as_geo(self):
        try:
            lat, lng = map(float, ast.literal_eval(self._value))
        except (SyntaxError, TypeError, ValueError):
            raise ValueError('not a geo field')
        # TODO: Check expected order (leaflet only is backwards?)
        return f'[{lat}, {lng}]'


class Row:
    """Group of fields keyed by name."""

    def __init__(self, fields):
        self._fields = fields

    def __repr__(self):
        return f'{self.__class__.__name__}({self._fields!r})'

    def __getitem__(self, key):
        return Cell(self._fields[key])
