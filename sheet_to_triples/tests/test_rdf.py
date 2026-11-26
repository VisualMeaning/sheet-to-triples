# Copyright 2021 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the rdf.py module of sheet-to-triples."""

import json
import unittest

import rdflib.term
from rdflib.namespace import OWL, RDF

from .. import rdf


class TestRDF(unittest.TestCase):

    @property
    def namespace_manager(self):
        return rdf._new_dataset().namespace_manager

    @property
    def resolver(self):
        return rdf._new_dataset().store.namespace

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
            ('_s', '_p', rdflib.Literal(
                'thing: "quotes"\nand newlines\tand tabs', lang='en')),
            ('_s', '_p', rdflib.Literal('\u043e', lang='bg')),
            ('_s', '_p', rdflib.Literal('л', lang='bg')),
            ('_s', '_p', rdflib.Literal('', lang='en')),
            ('_s', '_p', rdflib.Literal('["o1", "o2"]', lang='en')),
            ('_s', '_p', rdflib.Literal('{"o": "v"}', lang='en')),
        ]
        rdf.update_model_terms(model, triples)
        expected = [
            'o:_1', 'o', '"o"@en',
            '"thing: \\"quotes\\"\\nand newlines\\tand tabs"@en',
            '"\\u043e"@bg', '"\\u043b"@bg', '""@en',
            '["o1", "o2"]@en', '{"o": "v"}@en',
        ]
        self.assertEqual([t['obj'] for t in model['terms']], expected)

    def _graph(self, triples):
        return rdf.graph_from_triples(
            (rdflib.URIRef(s), rdflib.URIRef(p), o) for s, p, o in triples)

    def _terms(self, triples):
        return [{'subj': s, 'pred': p, 'obj': o} for s, p, o in triples]

    def test_terms_from_triples_ordering(self):
        """Ordered by subject, predicate, then object, never by input."""
        triples = [
            ('test_subj1', 'test_pred2', rdflib.Literal('test_obj')),
            ('test_subj1', 'test_pred1', rdflib.Literal('test_obj2')),
            ('test_subj2', 'test_pred1', rdflib.Literal('test_obj')),
            ('test_subj1', 'test_pred1', rdflib.Literal('test_obj1')),
        ]
        expected = self._terms([
            ('test_subj1', 'test_pred1', 'test_obj1'),
            ('test_subj1', 'test_pred1', 'test_obj2'),
            ('test_subj1', 'test_pred2', 'test_obj'),
            ('test_subj2', 'test_pred1', 'test_obj'),
        ])
        for ordering in (triples, triples[::-1]):
            with self.subTest(ordering=ordering):
                terms = rdf.terms_from_triples(self._graph(ordering))
                self.assertEqual(terms, expected)

    def test_terms_from_triples_ordinal_first(self):
        ordinal = str(rdf.VM.asOrdinal)
        triples = [
            ('http://a.test/1', 'p', rdflib.Literal('x')),
            ('http://b.test/1', ordinal, rdflib.Literal('2')),
            ('http://c.test/1', ordinal, rdflib.Literal('1.5')),
        ]
        terms = rdf.terms_from_triples(self._graph(triples))
        self.assertEqual(
            [t['subj'] for t in terms],
            ['http://c.test/1', 'http://b.test/1', 'http://a.test/1'])

    def test_terms_from_triples_excludes_bnodes(self):
        graph = rdf.graph_from_triples([
            (rdflib.BNode(), rdflib.URIRef('p'), rdflib.Literal('o')),
            (rdflib.URIRef('s'), rdflib.URIRef('p'), rdflib.BNode()),
            (rdflib.URIRef('s'), rdflib.URIRef('p'), rdflib.Literal('o')),
        ])
        self.assertEqual(
            rdf.terms_from_triples(graph), self._terms([('s', 'p', 'o')]))

    def test_terms_from_triples_same_serialisation_once(self):
        """Distinct rdflib terms that serialise the same give one term."""
        graph = self._graph([
            ('s', 'p', rdflib.Literal('http://o.test')),
            ('s', 'p', rdflib.URIRef('http://o.test')),
        ])
        self.assertEqual(
            rdf.terms_from_triples(graph),
            self._terms([('s', 'p', 'http://o.test')]))

    def test_terms_from_triples_language_tags(self):
        graph = self._graph([('s', 'p', rdflib.Literal('o', lang='en'))])
        self.assertEqual(
            rdf.terms_from_triples(graph), self._terms([('s', 'p', '"o"@en')]))

    def test_functional_properties(self):
        graph = rdf.graph_from_triples([
            (rdflib.URIRef('p1'), RDF.type, OWL.FunctionalProperty),
            (rdflib.URIRef('p2'), RDF.type, OWL.ObjectProperty),
        ])
        self.assertEqual(
            rdf.functional_properties(graph), {rdflib.URIRef('p1')})

    def test_new_graph_namespace_bindings(self):
        """Standalone graph has bindings, as used by other tools."""
        graph = rdf._new_graph()
        self.assertNotIsInstance(graph, rdflib.Dataset)
        self.assertEqual(
            dict(graph.namespaces())['vm'], rdflib.URIRef(str(rdf.VM)))

    def test_graph_from_model_in_dataset(self):
        dataset = rdf._new_dataset()
        identifier = rdflib.URIRef('urn:test:g')
        model = {'terms': [{'subj': 's', 'pred': 'p', 'obj': 'vm:o'}]}
        graph = rdf.graph_from_model(
            model, dataset=dataset, identifier=identifier)
        self.assertEqual(graph.identifier, identifier)
        self.assertEqual(
            set(dataset.graph(identifier)),
            {(rdflib.URIRef('s'), rdflib.URIRef('p'), rdf.VM.o)})

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

    def setUp(self):
        self.resolver = rdf.Resolver.from_graph(rdf.graph_from_triples(()))

    def test_from_identifier_known_iri_qname_returns_uriref(self):
        tests = {
            ('vm:Category', 'http://visual-meaning.com/rdf/Category'),
            ('gist:isCategorizedBy',
                 'https://ontologies.semanticarts.com/gist/isCategorizedBy'),
            ('rdf:type', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        }
        for value, expected in tests:
            with self.subTest(value=value):
                self.assertEqual(
                    self.resolver.from_identifier(value),
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
                self.assertEqual(
                    self.resolver.from_identifier(value),
                    rdflib.term.URIRef(value),
                )

    def test_from_identifier_unknown_url_returns_literal(self):
        value = 'https://bucket.s3.amazonaws.com/{z}-{x}-{y}.png'
        self.assertEqual(
            self.resolver.from_identifier(value),
            rdflib.term.Literal(value),
        )

    def test_from_identifier_aws_tiles_path_no_warning(self):
        tiles_src = 'https://bucket.s3.amazonaws.com/{z}-{x}-{y}.png'
        # bad spelling for compatibility with python 3.8 - ideally would use
        # self.assertNoLogs, but this was introduced in 3.10
        with self.assertRaises(AssertionError):
            with self.assertLogs(level='WARNING'):
                self.resolver.from_identifier(tiles_src)

    def test_from_identifier_string_returns_literal(self):
        self.assertEqual(
            self.resolver.from_identifier('test'),
            rdflib.Literal('test')
        )

    def test_from_identifier_meaningful_whitespace(self):
        self.assertEqual(
            self.resolver.from_identifier('* a\r\n  * a\t1\r\n  * a  2\r\n'),
            rdflib.Literal('* a\n  * a 1\n  * a 2\n')
        )

    def test_from_identifier_already_ident(self):
        term = rdflib.term.URIRef('http://visual-meaning.com/rdf/test')
        self.assertEqual(
            self.resolver.from_identifier(term),
            term
        )

    def test_from_identifier_sequencepath(self):
        term = self.resolver.from_identifier('vm:a / vm:b')
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
        self.assertEqual(
            self.resolver.from_identifier('"\u043e"@bg'),
            rdflib.Literal('\u043e', lang='bg')
        )

    def test_from_identifier_lang_obj(self):
        self.assertEqual(
            self.resolver.from_identifier('{"k": "v"}@en'),
            rdflib.Literal('{"k": "v"}', lang='en')
        )

    def test_from_identifier_lang_roundtrip(self):
        """
            Test the roundtrip workflow:
            string -> from_identifier -> Literal -> update_model_terms -> string.
        """
        test_texts = [
            ('simple text', 'en'),
            ('text\nwith\nnewlines', 'en'),
            ('text with "quotes"', 'fr'),
            ('text\twith\ttabs', 'de'),
            ('path\\with\\backslashes', 'es'),
            ('mixed: "quotes"\nand newlines\tand tabs', 'it'),
            ('', 'en'),
            ('о', 'bg'), # cyrillic o
            ('л', 'bg'),
        ]

        for text, lang in test_texts:
            with self.subTest(text=text, lang=lang):
                initial_string = json.dumps(text) + '@' + lang
                literal = self.resolver.from_identifier(initial_string)

                model = {'terms': []}
                triples = [('_s', '_p', literal)]
                rdf.update_model_terms(model, triples)

                resulting_string = model['terms'][0]['obj']
                self.assertEqual(initial_string, resulting_string)
