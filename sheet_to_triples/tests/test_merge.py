# Copyright 2026 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Unittests for the merge.py module of sheet-to-triples.

These only use plain rdflib graphs, not the runner or JSON model terms.
"""

import gc
import unittest

import rdflib
from rdflib.namespace import OWL, RDF

from .. import merge

EX = rdflib.Namespace('http://ex.test/')

ALL_UNIQUE = merge.UniquePredicates.all_except(())


def _graph(name, *triples):
    graph = rdflib.Graph(identifier=EX['graph/' + name])
    for triple in triples:
        graph.add(triple)
    return graph


def _lit(value):
    return rdflib.Literal(value)


class TestUniquePredicates(unittest.TestCase):

    def test_all_except(self):
        unique = merge.UniquePredicates.all_except({EX.many})
        self.assertIn(EX.one, unique)
        self.assertNotIn(EX.many, unique)

    def test_only(self):
        unique = merge.UniquePredicates.only({EX.one})
        self.assertIn(EX.one, unique)
        self.assertNotIn(EX.many, unique)

    def test_compares_strings_and_iris(self):
        unique = merge.UniquePredicates.all_except({str(EX.many)})
        self.assertNotIn(EX.many, unique)
        self.assertNotIn(str(EX.many), unique)
        unique = merge.UniquePredicates.only({EX.one})
        self.assertIn(str(EX.one), unique)


class TestMerge(unittest.TestCase):

    def test_empty(self):
        merged, report = merge.merge([], ALL_UNIQUE)
        self.assertEqual(len(merged), 0)
        self.assertFalse(report)

    def test_later_graph_wins(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('1')))
        g2 = _graph('g2', (EX.s, EX.p, _lit('2')))
        merged, _ = merge.merge([g1, g2], ALL_UNIQUE)
        self.assertEqual(set(merged), {(EX.s, EX.p, _lit('2'))})

        merged, _ = merge.merge([g2, g1], ALL_UNIQUE)
        self.assertEqual(set(merged), {(EX.s, EX.p, _lit('1'))})

    def test_highest_graph_with_value_wins(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('1')))
        g2 = _graph('g2', (EX.s, EX.p, _lit('2')))
        g3 = _graph('g3', (EX.other, EX.p, _lit('3')))
        merged, _ = merge.merge([g1, g2, g3], ALL_UNIQUE)
        self.assertEqual(set(merged), {
            (EX.s, EX.p, _lit('2')),
            (EX.other, EX.p, _lit('3')),
        })

    def test_dropped_reported_with_graphs(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('1')))
        g2 = _graph('g2', (EX.s, EX.p, _lit('2')))
        _, report = merge.merge([g1, g2], ALL_UNIQUE)
        self.assertEqual(report.dropped, [merge.Dropped(
            EX.s, EX.p, _lit('1'), g1.identifier, _lit('2'), g2.identifier)])
        self.assertEqual(report.self_conflicts, [])
        self.assertTrue(report)

    def test_dropped_from_each_lower_graph(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('1')))
        g2 = _graph('g2', (EX.s, EX.p, _lit('1')))
        g3 = _graph('g3', (EX.s, EX.p, _lit('3')))
        _, report = merge.merge([g1, g2, g3], ALL_UNIQUE)
        self.assertEqual(
            [(d.obj, d.graph, d.kept_graph) for d in report.dropped],
            [
                (_lit('1'), g1.identifier, g3.identifier),
                (_lit('1'), g2.identifier, g3.identifier),
            ])

    def test_same_triple_in_several_graphs_once(self):
        triple = (EX.s, EX.p, _lit('1'))
        g1 = _graph('g1', triple)
        g2 = _graph('g2', triple, (EX.s, EX.q, _lit('x')))
        g3 = _graph('g3', triple)
        for unique in (ALL_UNIQUE, merge.UniquePredicates.only(())):
            with self.subTest(unique=unique):
                merged, report = merge.merge([g1, g2, g3], unique)
                self.assertEqual(
                    sorted(merged), sorted([triple, (EX.s, EX.q, _lit('x'))]))
                self.assertFalse(report)

    def test_non_unique_union(self):
        g1 = _graph('g1', (EX.s, EX.many, _lit('1')), (EX.s, EX.one, _lit('a')))
        g2 = _graph('g2', (EX.s, EX.many, _lit('2')), (EX.s, EX.one, _lit('b')))
        unique = merge.UniquePredicates.all_except({EX.many})
        merged, report = merge.merge([g1, g2], unique)
        self.assertEqual(set(merged), {
            (EX.s, EX.many, _lit('1')),
            (EX.s, EX.many, _lit('2')),
            (EX.s, EX.one, _lit('b')),
        })
        self.assertEqual(len(report.dropped), 1)

    def test_only_given_predicates_unique(self):
        g1 = _graph('g1', (EX.s, EX.one, _lit('1')), (EX.s, EX.many, _lit('1')))
        g2 = _graph('g2', (EX.s, EX.one, _lit('2')), (EX.s, EX.many, _lit('2')))
        unique = merge.UniquePredicates.only({EX.one})
        merged, _ = merge.merge([g1, g2], unique)
        self.assertEqual(set(merged), {
            (EX.s, EX.one, _lit('2')),
            (EX.s, EX.many, _lit('1')),
            (EX.s, EX.many, _lit('2')),
        })

    def test_self_conflict_reported(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('a')), (EX.s, EX.p, _lit('b')))
        merged, report = merge.merge([g1], ALL_UNIQUE)
        [conflict] = report.self_conflicts
        self.assertEqual(conflict.graph, g1.identifier)
        self.assertEqual((conflict.subject, conflict.predicate), (EX.s, EX.p))
        self.assertEqual(set(conflict.objs), {_lit('a'), _lit('b')})
        self.assertEqual(set(merged), {(EX.s, EX.p, conflict.kept)})
        self.assertEqual(report.dropped, [])

    def test_self_conflict_deterministic(self):
        values = [_lit('b'), EX.c, _lit('a'), rdflib.Literal('a', lang='en')]
        results = set()
        for ordering in (values, values[::-1], values[1:] + values[:1]):
            g1 = _graph('g1', *((EX.s, EX.p, o) for o in ordering))
            merged, report = merge.merge([g1], ALL_UNIQUE)
            results.add((tuple(merged), report.self_conflicts[0]))
        self.assertEqual(len(results), 1)

    def test_self_conflict_in_overridden_graph(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('a')), (EX.s, EX.p, _lit('b')))
        g2 = _graph('g2', (EX.s, EX.p, _lit('a')))
        merged, report = merge.merge([g1, g2], ALL_UNIQUE)
        self.assertEqual(set(merged), {(EX.s, EX.p, _lit('a'))})
        self.assertEqual(report.self_conflicts, [merge.SelfConflict(
            g1.identifier, EX.s, EX.p, (_lit('a'), _lit('b')), None)])
        # Same value as the kept one is not a drop, the other one is
        self.assertEqual(report.dropped, [merge.Dropped(
            EX.s, EX.p, _lit('b'), g1.identifier, _lit('a'), g2.identifier)])

    def test_self_conflict_overrides_lower_graph(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('x')))
        g2 = _graph('g2', (EX.s, EX.p, _lit('a')), (EX.s, EX.p, _lit('b')))
        merged, report = merge.merge([g1, g2], ALL_UNIQUE)
        [conflict] = report.self_conflicts
        self.assertEqual(conflict.graph, g2.identifier)
        self.assertIn(conflict.kept, (_lit('a'), _lit('b')))
        self.assertEqual(set(merged), {(EX.s, EX.p, conflict.kept)})
        self.assertEqual(report.dropped, [merge.Dropped(
            EX.s, EX.p, _lit('x'), g1.identifier,
            conflict.kept, g2.identifier)])

    def test_resolve_same(self):
        g1 = _graph(
            'g1',
            (EX.old, EX.p, _lit('1')),
            (EX.old, EX.q, _lit('kept')),
            (EX.ref, EX.links, EX.old),
        )
        g2 = _graph(
            'g2',
            (EX.new, OWL.sameAs, EX.old),
            (EX.new, EX.p, _lit('2')),
        )
        merged, report = merge.merge([g1, g2], ALL_UNIQUE, resolve_same=True)
        self.assertEqual(set(merged), {
            (EX.new, EX.p, _lit('2')),
            (EX.new, EX.q, _lit('kept')),
            (EX.ref, EX.links, EX.new),
        })
        self.assertEqual(
            report.aliases, [merge.Alias(EX.old, EX.new, g2.identifier)])
        self.assertEqual(
            [(d.subject, d.obj) for d in report.dropped],
            [(EX.new, _lit('1'))])

    def test_resolve_same_literal_alias(self):
        """Model terms may load IRIs in unknown namespaces as literals."""
        g1 = _graph(
            'g1',
            (EX.new, OWL.sameAs, _lit('urn:old')),
            (rdflib.URIRef('urn:old'), EX.p, _lit('1')),
        )
        merged, _ = merge.merge([g1], ALL_UNIQUE, resolve_same=True)
        self.assertEqual(set(merged), {(EX.new, EX.p, _lit('1'))})

    def test_resolve_same_off_keeps_same_as(self):
        g1 = _graph('g1', (EX.new, OWL.sameAs, EX.old), (EX.old, EX.p, _lit('1')))
        merged, report = merge.merge([g1], ALL_UNIQUE)
        self.assertEqual(set(merged), set(g1))
        self.assertEqual(report.aliases, [])

    def test_bnodes_renamed_apart(self):
        b = rdflib.BNode('b0')
        g1 = _graph('g1', (b, EX.p, _lit('1')))
        g2 = _graph('g2', (b, EX.p, _lit('2')))
        merged, report = merge.merge([g1, g2], ALL_UNIQUE)
        self.assertEqual(len(merged), 2)
        self.assertEqual(len(set(merged.subjects())), 2)
        self.assertFalse(report)

    def test_bnodes_consistent_within_graph(self):
        b = rdflib.BNode('b0')
        g1 = _graph('g1', (EX.s, EX.has, b), (b, EX.p, _lit('1')))
        merged, _ = merge.merge([g1], ALL_UNIQUE)
        [node] = merged.objects(EX.s, EX.has)
        self.assertIsInstance(node, rdflib.BNode)
        self.assertNotEqual(node, b)
        self.assertEqual(merged.value(node, EX.p), _lit('1'))

    def test_prefixes_carried_through(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('1')))
        g1.bind('ex', EX)
        g2 = _graph('g2', (EX.s, RDF.type, EX.Thing))
        g2.bind('other', 'http://other.test/')
        merged, _ = merge.merge([g1, g2], ALL_UNIQUE)
        namespaces = dict(merged.namespaces())
        self.assertEqual(namespaces['ex'], rdflib.URIRef(EX))
        self.assertEqual(
            namespaces['other'], rdflib.URIRef('http://other.test/'))

    def test_inputs_unchanged(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('1')))
        g2 = _graph('g2', (EX.s, EX.p, _lit('2')), (EX.s, OWL.sameAs, EX.o))
        before = [set(g1), set(g2)]
        merge.merge([g1, g2], ALL_UNIQUE, resolve_same=True)
        self.assertEqual([set(g1), set(g2)], before)

    def test_accepts_dataset_named_graphs(self):
        dataset = rdflib.Dataset()
        g1 = dataset.graph(EX['graph/g1'])
        g1.add((EX.s, EX.p, _lit('1')))
        g2 = dataset.graph(EX['graph/g2'])
        g2.add((EX.s, EX.p, _lit('2')))
        merged, report = merge.merge([g1, g2], ALL_UNIQUE)
        self.assertEqual(set(merged), {(EX.s, EX.p, _lit('2'))})
        self.assertEqual(report.dropped[0].graph, EX['graph/g1'])

    def test_into_target(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('1')), (EX.s, EX.q, _lit('x')))
        g2 = _graph('g2', (EX.s, EX.p, _lit('2')))
        target = set()
        merged, report = merge.merge([g1, g2], ALL_UNIQUE, into=target)
        self.assertIs(merged, target)
        self.assertEqual(target, {
            (EX.s, EX.p, _lit('2')),
            (EX.s, EX.q, _lit('x')),
        })
        self.assertEqual(len(report.dropped), 1)

    def test_many_graphs(self):
        """Precedence holds past any fixed width, such as 64 graphs."""
        graphs = [
            _graph(f'g{n}', (EX.s, EX.p, _lit(str(n))), (EX[f's{n}'], EX.p, _lit('x')))
            for n in range(200)
        ]
        graphs[50].add((EX.s, EX.p, _lit('extra')))
        merged, report = merge.merge(graphs, ALL_UNIQUE)
        self.assertEqual(merged.value(EX.s, EX.p), _lit('199'))
        self.assertEqual(len(merged), 201)
        self.assertEqual(
            [d.graph for d in report.dropped][:2],
            [EX['graph/g0'], EX['graph/g1']])
        self.assertEqual(len(report.dropped), 200)
        self.assertEqual(
            [(c.graph, c.kept) for c in report.self_conflicts],
            [(EX['graph/g50'], None)])

    def test_gc_state_restored(self):
        g1 = _graph('g1', (EX.s, EX.p, _lit('1')))
        self.assertTrue(gc.isenabled())
        merge.merge([g1], ALL_UNIQUE)
        self.assertTrue(gc.isenabled())
        gc.disable()
        try:
            merge.merge([g1], ALL_UNIQUE)
            self.assertFalse(gc.isenabled())
        finally:
            gc.enable()
