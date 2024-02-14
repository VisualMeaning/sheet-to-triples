# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the rdf.py module of sheet-to-triples."""

import io
import unittest
from unittest import mock

import rdflib.term

from .. import rdf


class TestRDF(unittest.TestCase):

    @property
    def namespace_manager(self):
        return rdf._new_graph().namespace_manager

    @property
    def resolver(self):
        return rdf._new_graph().store.namespace

    def test_from_qname(self):
        term = rdf.from_qname('owl:test', self.resolver)
        self.assertIsInstance(term, rdflib.term.URIRef)
        self.assertEqual(str(term), 'http://www.w3.org/2002/07/owl#test')

    def test_from_foaf_phone(self):
        """Not fully standardised foaf qname still resolves."""
        term = rdf.from_qname('foaf:phone', self.resolver)
        self.assertIsInstance(term, rdflib.term.URIRef)
        self.assertEqual(str(term), 'http://xmlns.com/foaf/0.1/phone')

    def test_from_qname_prefix_http(self):
        term = rdf.from_qname('http://test.test', self.resolver)
        self.assertIsInstance(term, rdflib.term.URIRef)
        self.assertEqual(str(term), 'http://test.test')

    def test_from_qname_unknown_prefix(self):
        with self.assertRaises(ValueError) as ctx:
            rdf.from_qname('unk:test', self.resolver)
        self.assertEqual(str(ctx.exception), 'unknown prefix: unk')

    def test_relates_geo_name_true(self):
        for path in ('atGeoPoint', 'atGeoPoly', 'name'):
            term = {'pred': 'http://visual-meaning.com/rdf/' + path}
            with self.subTest(pred=term['pred']):
                self.assertTrue(rdf.relates_geo_name(term))

    def test_relates_geo_name_false(self):
        for path in ('http://visual-meaning.com/rdf/test', 'test/atGeoPoint'):
            term = {'pred': path}
            with self.subTest(pred=term['pred']):
                self.assertFalse(rdf.relates_geo_name(term))

    def test_relates_issue_true(self):
        self.assertTrue(
            rdf.relates_issue({'subj': 'http://visual-meaning.com/rdf/test'})
        )

    def test_relates_issue_false(self):
        self.assertFalse(
            rdf.relates_issue(
                {'subj': 'http://visual-meaning.com/rdf/issues/'},
            )
        )

    def test_purge_terms(self):
        model = {
            'terms': [
                {'obj': 'http://visual-meaning.com/rdf/test'},
                {'obj': 'http://visual-meaning.com/rdf/whitespace   '},
                {'obj': 'test'}
            ]
        }

        def retain(x):
            return x['obj'].startswith('http://visual-meaning.com/rdf/')

        rdf.purge_terms(model, retain, False)

        expected = {
            'terms': [
                {'obj': 'http://visual-meaning.com/rdf/test'},
                {'obj': 'http://visual-meaning.com/rdf/whitespace '},
            ]
        }
        self.assertEqual(model, expected)

    def test_graph_from_model(self):
        model = {
            'terms': [
                {
                    'subj': 'test_subj',
                    'pred': 'test_pred',
                    'obj': 'test_obj',
                }
            ]
        }
        graph = rdf.graph_from_model(model)

        instance_values = [
            (next(graph.subjects()), rdflib.term.URIRef, 'test_subj'),
            (next(graph.predicates()), rdflib.term.URIRef, 'test_pred'),
            (next(graph.objects()), rdflib.term.Literal, 'test_obj'),
        ]
        for test_value, instance, expected_value in instance_values:
            with self.subTest(value=expected_value):
                self.assertIsInstance(test_value, instance)
                self.assertEqual(str(test_value), expected_value)

    def test_graph_namespace_bindings(self):
        expected = {
            ('vm', rdflib.term.URIRef('http://visual-meaning.com/rdf/')),
            ('vmhe', rdflib.term.URIRef('http://visual-meaning.com/rdf/HE/')),
            ('foaf', rdflib.term.URIRef('http://xmlns.com/foaf/0.1/')),
            ('skos',
                rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#')),
            ('owl', rdflib.term.URIRef('http://www.w3.org/2002/07/owl#'))
        }

        graph = rdf.graph_from_model({'terms': []})
        ns = set(graph.namespaces())
        self.assertTrue(expected.issubset(ns))

    def test_update_model_terms(self):
        model = {'terms': []}
        rdf.update_model_terms(model, [('test_subj', 'test_pred', 'test_obj')])
        expected = {
            'terms': [
                {
                    'subj': 'test_subj',
                    'pred': 'test_pred',
                    'obj': 'test_obj',
                }
            ]
        }
        self.assertEqual(model, expected)

    def test_update_model_terms_exclude_bnodes(self):
        """Filter triples out if EITHER the subj or obj are type BNodes."""
        model = {'terms': []}
        bnodes = [
            (rdflib.term.BNode('subj'), 'pred', 'obj'),
            ('subj', 'pred', rdflib.term.BNode('obj')),
        ]
        rdf.update_model_terms(model, bnodes)
        expected = {'terms': []}
        self.assertEqual(model, expected)

    def test_update_model_terms_language_tags(self):
        """Literals with language tags have special serialisation to terms."""
        model = {'terms': []}
        triples = [
            ('_s', '_p', rdflib.URIRef('o:_1')),
            # Not testing rdflib.Literal(1) as should maybe change behaviour?
            ('_s', '_p', rdflib.Literal('o')),
            ('_s', '_p', rdflib.Literal('o', lang='en')),
            ('_s', '_p', rdflib.Literal('\u043e', lang='bg')),
            ('_s', '_p', rdflib.Literal('', lang='en')),
            ('_s', '_p', rdflib.Literal('["o1", "o2"]', lang='en')),
            ('_s', '_p', rdflib.Literal('{"o": "v"}', lang='en')),
        ]
        rdf.update_model_terms(model, triples)
        expected = [
            'o:_1', 'o', '"o"@en', '"\u043e"@bg', '""@en', '["o1", "o2"]@en',
            '{"o": "v"}@en',
        ]
        self.assertEqual([t['obj'] for t in model['terms']], expected)

    def _model_from_triples(self, triples):
        terms = [{'subj': s, 'pred': p, 'obj': o} for s, p, o in triples]
        return {'terms': terms}

    def test_normalise_model_unique_predicate(self):
        triples = [
            ('test_subj', 'test_pred', 'test_obj'),
            ('test_subj', 'test_pred', 'test_obj2')
        ]
        model = self._model_from_triples(triples)

        with mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
            rdf.normalise_model(
                model, self.namespace_manager, [], False, False)

        # it should take the last recorded triple in the list
        expected_triples = [
            ('test_subj', 'test_pred', 'test_obj2'),
        ]
        self.assertEqual(model, self._model_from_triples(expected_triples))
        self.assertRegex(fake_out.getvalue(), r'^# dropping .*$')

    def test_normalise_model_non_unique_predicate(self):
        triples = [
            ('test_subj', 'test_pred', 'test_obj'),
            ('test_subj', 'test_pred', 'test_obj'),
            ('test_subj', 'test_pred', 'test_obj2'),
        ]
        model = self._model_from_triples(triples)
        rdf.normalise_model(
            model, self.namespace_manager, ['test_pred'], False, False)
        # should allow multiple obj values for one predicate
        expected_triples = [
            ('test_subj', 'test_pred', 'test_obj'),
            ('test_subj', 'test_pred', 'test_obj2'),
        ]
        self.assertEqual(model, self._model_from_triples(expected_triples))

    def test_normalise_model_resolve_same(self):
        triples = [
            ('test_subj', 'test_pred', 'test_obj'),
            ('test_subj', 'test_pred2', 'test_obj'),
            ('test_subj', 'http://www.w3.org/2002/07/owl#sameAs',
                'test_subj2'),
            ('test_subj2', 'test_pred2', 'test_obj2'),
        ]
        model = self._model_from_triples(triples)
        with mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
            rdf.normalise_model(model, self.namespace_manager, [], True, False)
        expected_triples = [
            ('test_subj', 'test_pred', 'test_obj'),
            ('test_subj', 'test_pred2', 'test_obj2'),
        ]
        self.assertEqual(model, self._model_from_triples(expected_triples))
        self.assertRegex(fake_out.getvalue(), r'^# dropping .*$')

    def test_normalise_model_ordering(self):
        triples = [
            ('test_subj1', 'test_pred2', 'test_obj'),
            ('test_subj1', 'test_pred1', 'test_obj2'),
            ('test_subj2', 'test_pred1', 'test_obj'),
            ('test_subj1', 'test_pred1', 'test_obj1'),
        ]
        model = self._model_from_triples(triples)
        rdf.normalise_model(
            model, self.namespace_manager, ['test_pred1'], False, False)

        expected_triples = [
            ('test_subj1', 'test_pred1', 'test_obj2'),
            ('test_subj1', 'test_pred1', 'test_obj1'),
            ('test_subj1', 'test_pred2', 'test_obj'),
            ('test_subj2', 'test_pred1', 'test_obj'),
        ]
        self.assertEqual(model, self._model_from_triples(expected_triples))

    def test_graph_from_triples(self):
        triples = [
            (
                rdflib.term.URIRef('test_subj'),
                rdflib.term.URIRef('test_pred'),
                rdflib.term.Literal('test_obj'),
            )
        ]
        graph = rdf.graph_from_triples(triples)

        instance_values = [
            (next(graph.subjects()), rdflib.term.URIRef, 'test_subj'),
            (next(graph.predicates()), rdflib.term.URIRef, 'test_pred'),
            (next(graph.objects()), rdflib.term.Literal, 'test_obj'),
        ]
        for test_value, instance, expected_value in instance_values:
            with self.subTest(value=expected_value):
                self.assertIsInstance(test_value, instance)
                self.assertEqual(str(test_value), expected_value)


class TestResolver(unittest.TestCase):

    @property
    def graph(self):
        return rdf._new_graph()

    def test_from_identifier_known_iri_qname_returns_uriref(self):
        tests = {
            ('vm:Category', 'http://visual-meaning.com/rdf/Category'),
            ('gist:isCategorizedBy',
                 'https://ontologies.semanticarts.com/gist/isCategorizedBy'),
            ('rdf:type', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        }
        for value, expected in tests:
            with self.subTest(value=value):
                resolver = rdf.Resolver(self.graph)
                self.assertEqual(
                    resolver.from_identifier(value),
                    rdflib.term.URIRef(expected),
                )

    def test_from_identifier_known_iri_url_returns_uriref(self):
        tests = {
            'http://visual-meaning.com/rdf/Category',
            'https://ontologies.semanticarts.com/gist/isCategorizedBy',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
        }
        for value in tests:
            with self.subTest(value=value):
                resolver = rdf.Resolver(self.graph)
                self.assertEqual(
                    resolver.from_identifier(value),
                    rdflib.term.URIRef(value),
                )

    def test_from_identifier_unknown_url_returns_literal(self):
        tests = {
            'https://bucket.s3.amazonaws.com/{z}-{x}-{y}.png#background:#fff',
        }
        for value in tests:
            with self.subTest(value=value):
                resolver = rdf.Resolver(self.graph)
                self.assertEqual(
                    resolver.from_identifier(value),
                    rdflib.term.Literal(value),
                )

    def test_from_identifier_aws_tiles_path_no_warning(self):
        resolver = rdf.Resolver(self.graph)
        tiles_src = 'https://bucket.s3.amazonaws.com/{z}-{x}-{y}.png#background:#fff'
        # bad spelling for compatibility with python 3.8 - ideally would use
        # self.assertNoLogs, but this was introduced in 3.10
        with self.assertRaises(AssertionError):
            with self.assertLogs(level='WARNING'):
                resolver.from_identifier(tiles_src)

    def test_from_identifier_string_returns_literal(self):
        resolver = rdf.Resolver(self.graph)
        self.assertEqual(
            resolver.from_identifier('test'),
            rdflib.Literal('test')
        )

    def test_from_identifier_meaningful_whitespace(self):
        resolver = rdf.Resolver(self.graph)
        self.assertEqual(
            resolver.from_identifier('* a\r\n  * a\t1\r\n  * a  2\r\n'),
            rdflib.Literal('* a\n  * a 1\n  * a 2\n')
        )

    def test_from_identifier_already_ident(self):
        resolver = rdf.Resolver(self.graph)
        term = rdflib.term.URIRef('http://visual-meaning.com/rdf/test')
        self.assertEqual(
            resolver.from_identifier(term),
            term
        )

    def test_from_identifier_sequencepath(self):
        resolver = rdf.Resolver(self.graph)
        term = resolver.from_identifier('vm:a / vm:b')
        expected = [
            'http://visual-meaning.com/rdf/a',
            'http://visual-meaning.com/rdf/b',
        ]
        self.assertIsInstance(term, rdflib.paths.SequencePath)
        self.assertEqual(
            [str(p) for p in term.args],
            expected
        )

    def test_from_identifier_lang_str(self):
        resolver = rdf.Resolver(self.graph)
        self.assertEqual(
            resolver.from_identifier('"\u043e"@bg'),
            rdflib.Literal('\u043e', lang='bg')
        )

    def test_from_identifier_lang_obj(self):
        resolver = rdf.Resolver(self.graph)
        self.assertEqual(
            resolver.from_identifier('{"k": "v"}@en'),
            rdflib.Literal('{"k": "v"}', lang='en')
        )
