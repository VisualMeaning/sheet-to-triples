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
        self.assertEqual(field.Cell('Brazil').as_country_code, 'br')

    def test_as_country_code_fuzzy(self):
        self.assertEqual(field.Cell('Russia').as_country_code, 'ru')

    def test_as_country_code_bad_values(self):
        errors_cases = (
            (None, ValueError),
            ('notfound', LookupError),
            ('   ', ValueError),
        )
        for value, error in errors_cases:
            with self.subTest(value=value):
                with self.assertRaises(error):
                    field.Cell(value).as_country_code

    def test_exists_true(self):
        self.assertTrue(field.Cell('exists').exists)

    def test_exists_false(self):
        self.assertFalse(field.Cell(None).exists)

    def test_not_exists_true(self):
        self.assertTrue(field.Cell(None).not_exists)

    def test_not_exists_false(self):
        self.assertFalse(field.Cell('exists').not_exists)


class RowTestCase(unittest.TestCase):

    def test_cols_disjoint_true(self):
        row = field.Row({'col1': 'a', 'col2': 'b'})
        self.assertTrue(row.cols_disjoint(['col3', 'col4']))

    def test_cols_disjoint_false(self):
        row = field.Row({'col1': 'a', 'col2': 'b'})
        self.assertFalse(row.cols_disjoint(['col2', 'col3']))

    def test_melt(self):
        self.maxDiff = None
        row = field.Row({'col1': 'a', 'col2': 'b', 'col3': 'c'})

        expected = [
            {
                'col1': 'a', 'col2': 'b', 'col3': 'c',
                '_melt_colname': 'col2', '_melt_value': 'b', '_has_melt': True
            },
            {
                'col1': 'a', 'col2': 'b', 'col3': 'c',
                '_melt_colname': 'col3', '_melt_value': 'c', '_has_melt': True
            },
        ]
        self.assertEqual(
            [r for r in row.melt(['col2', 'col3'])],
            [field.Row(r) for r in expected]
        )

    def test_has_melt_false_if_no_melt_cols(self):
        row = field.Row({'col1': 'a', 'col2': 'b', 'col3': 'c'})
        expected = [
            {'col1': 'a', 'col2': 'b', 'col3': 'c', '_has_melt': False}
        ]
        self.assertEqual(
            [r for r in row.melt(['col4'])],
            [field.Row(r) for r in expected]
        )
