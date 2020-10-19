# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Interfaces for mapping from tabular data."""

import ast
import re


class Cell:
    """Single field value for interpretation in context."""

    _pattern = re.compile(r'\W+')

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return f'{self.__class__.__name__}({self._value!r})'

    def __str__(self):
        return self._value

    @property
    def as_slug(self):
        return self._pattern.sub('-', self._value.replace('&', 'and')).lower()

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
