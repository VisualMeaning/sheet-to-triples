# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the field.py module of sheet-to-triples."""

import datetime
import unittest

from .. import field


def _dt_from_str(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d')


class CellTestCase(unittest.TestCase):

    def test_as_slug(self):
        self.assertEqual(
            field.Cell('  Some?letters+<&>characters  ').as_slug,
            'some-letters-and-characters'
        )

    def test_as_slug_empty(self):
        with self.assertRaises(ValueError):
            field.Cell('').as_slug

    def test_as_uc(self):
        self.assertEqual(
            field.Cell('   Some?letters+<and>characters   ').as_uc,
            'SomeLettersAndCharacters'
        )

    def test_as_uc_empty(self):
        with self.assertRaises(ValueError):
            field.Cell('').as_uc

    def test_as_json(self):
        self.assertEqual(
            field.Cell({'list': ['é', 1, None]}).as_json,
            '{"list":["é",1,null]}'
        )

    def test_as_json_empty(self):
        with self.assertRaises(ValueError):
            field.Cell('').as_json

    def test_as_text(self):
        self.assertEqual(
            field.Cell(1).as_text,
            '1'
        )

    def test_as_text_empty(self):
        with self.assertRaises(ValueError):
            field.Cell('   ').as_text

    def test_as_capital(self):
        self.assertEqual(
            field.Cell('   shared   ').as_capital,
            'vm:capitalTypes/sharedFinancial'
        )

    def test_as_capital_bad_values(self):
        errors_cases = (
            (None, ValueError),
            ('notfound', TypeError),
            ('   ', ValueError),
        )
        for value, error in errors_cases:
            with self.subTest(value=value):
                with self.assertRaises(error):
                    field.Cell(value).as_capital

    def test_as_capital_effect(self):
        self.assertEqual(
            field.Cell('Painpoint').as_capital_effect,
            'vm:harmsCapitalType'
        )

    def test_as_capital_effect_bad_values(self):
        errors_cases = (
            (None, ValueError),
            ('notfound', TypeError),
            ('   ', ValueError),
        )
        for value, error in errors_cases:
            with self.subTest(value=value):
                with self.assertRaises(error):
                    field.Cell(value).as_capital_effect

    def test_as_type(self):
        self.assertEqual(
            field.Cell('   Painpoint   ').as_type,
            'vm:Painpoint'
        )

    def test_as_type_bad_values(self):
        errors_cases = (
            (None, ValueError),
            ('notfound', TypeError),
            ('   ', ValueError),
        )
        for value, error in errors_cases:
            with self.subTest(value=value):
                with self.assertRaises(error):
                    field.Cell(value).as_type

    def test_as_type_slug(self):
        self.assertEqual(
            field.Cell('Painpoint').as_type_slug,
            'painpoint'
        )

    def test_as_type_slug_bad_values(self):
        errors_cases = (
            (None, ValueError),
            ('notfound', TypeError),
            ('   ', ValueError),
        )
        for value, error in errors_cases:
            with self.subTest(value=value):
                with self.assertRaises(error):
                    field.Cell(value).as_type_slug

    def test_as_geo(self):
        self.assertEqual(
            field.Cell('(51.752660, -1.263416)').as_geo,
            '[51.75266, -1.263416]'
        )

    def test_as_geo_bad_values(self):
        for value in (1, None, 'not a geo'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    field.Cell(value).as_geo

    def test_as_date(self):
        self.assertEqual(
            field.Cell(_dt_from_str('2021-06-07')).as_date,
            '2021-06-07'
        )

    def test_as_date_or_text_is_date(self):
        self.assertEqual(
            field.Cell(_dt_from_str('2021-06-07')).as_date_or_text,
            '2021-06-07'
        )

    def test_as_date_or_text_is_text(self):
        self.assertEqual(
            field.Cell('7th June').as_date_or_text,
            '7th June'
        )

    def test_as_country_code(self):
        self.assertEqual(
            field.Cell('Brazil').as_country_code,
            'BR'
        )

    def test_as_country_code_bad_values(self):
        errors_cases = (
            (None, ValueError),
            ('notfound', AttributeError),
            ('   ', ValueError),
        )
        for value, error in errors_cases:
            with self.subTest(value=value):
                with self.assertRaises(error):
                    field.Cell(value).as_country_code
