# Copyright 2026 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Merge ranked RDF graphs into one graph, resolving unique predicate values.

Precedence comes only from the order the graphs are given in. For a unique
predicate, the value from the highest ranked (last) graph wins.

Triples within one graph have no order, so a graph with several values for
one unique (subject, predicate) contradicts itself. That is reported as a
self conflict but a value is still picked deterministically, so output is
stable. Nothing should depend on which value that is.
"""

from dataclasses import dataclass, field
from typing import NamedTuple, Optional

import rdflib
from rdflib.namespace import OWL
from rdflib.term import BNode, Literal, URIRef, Node


class UniquePredicates:
    def __init__(self, iris, complement=False):
        self._iris = set(map(str, iris))
        self._complement = complement

    @classmethod
    def only(cls, iris):
        return cls(iris)

    @classmethod
    def all_except(cls, iris):
        return cls(iris, complement=True)

    def __contains__(self, predicate):
        return (str(predicate) in self._iris) != self._complement

    def __repr__(self):
        kind = 'all_except' if self._complement else 'only'
        return f'{self.__class__.__name__}.{kind}({sorted(self._iris)!r})'


class Dropped(NamedTuple):
    subject: Node
    predicate: Node
    obj: Node
    graph: Node
    kept_obj: Node
    kept_graph: Node


class SelfConflict(NamedTuple):
    graph: Node
    subject: Node
    predicate: Node
    objs: tuple[Node, ...]
    kept: Optional[Node]


class Kept(NamedTuple):
    obj: Node
    graph: Node


class Alias(NamedTuple):
    alias: Node
    canonical: Node
    graph: Node


@dataclass
class ConflictReport:
    dropped: list[Dropped] = field(default_factory=list)
    self_conflicts: list[SelfConflict] = field(default_factory=list)
    aliases: list[Alias] = field(default_factory=list)

    def __bool__(self):
        return bool(self.dropped or self.self_conflicts)


def _order_key(term):
    # rdflib term ordering
    return term.n3()


def _pair_key(pair):
    return _order_key(pair[0]), _order_key(pair[1])


def _choose(objs):
    # pick one deterministically
    try:
        return max(objs)
    except TypeError:
        return max(objs, key=_order_key)


def _aliasable(term):
    # Model JSON loads IRIs outside known namespaces as plain literals, so
    # match those too, as the string based normalisation always did.
    return isinstance(term, URIRef) or (
        isinstance(term, Literal) and not term.language and not term.datatype)


def _collect_aliases(graphs, report):
    # A higher ranked graph wins if one alias is given several canonical IRIs.
    aliases = {}
    for graph in graphs:
        same = sorted(graph.subject_objects(OWL.sameAs), key=_pair_key)
        for canonical, alias in same:
            aliases[str(alias)] = canonical
            report.aliases.append(Alias(alias, canonical, graph.identifier))
    return aliases


def _renamer(aliases):
    """Make function renaming terms of one graph before they are combined.

    Blank nodes are renamed apart so ones from different graphs never fuse,
    and when aliases are given, those terms are replaced by canonical ones.
    """
    bnodes = {}

    def rename(term):
        if isinstance(term, BNode):
            b = bnodes.get(term)
            if b is None:
                b = bnodes[term] = BNode()
            return b
        if aliases and _aliasable(term):
            return aliases.get(str(term), term)
        return term

    return rename


def _group_unique(graph, rename, is_unique, skip, merged):
    """Group one graph's unique predicate values by (subject, predicate).

    It is a single iteration to append the non-unique predicate triples
    into the resulting container as well.
    """
    by_key = {}
    for s, p, o in graph:
        if p == skip:
            continue
        s, p, o = rename(s), rename(p), rename(o)
        if not is_unique(p):
            merged.add((s, p, o))
            continue
        key = (s, p)
        prev = by_key.get(key)
        if prev is None:
            by_key[key] = o
        elif isinstance(prev, set):
            prev.add(o)
        elif prev != o:
            by_key[key] = {prev, o}
    return by_key


def _unique_checker(unique_predicates):
    cache = {}

    def is_unique(predicate):
        unique = cache.get(predicate)
        if unique is None:
            unique = cache[predicate] = predicate in unique_predicates
        return unique

    return is_unique


def _sorted_objs(objs):
    return tuple(sorted(objs, key=_order_key))


def _in_report_order(keyed):
    """Report items from (key, rank, item) tuples, ordered by key then rank."""
    keyed.sort(key=lambda entry: (_pair_key(entry[0]), entry[1]))
    return [item for _, _, item in keyed]


def _bind_namespaces(target, graphs):
    for graph in graphs:
        for prefix, namespace in graph.namespaces():
            target.bind(prefix, namespace, override=False)


def merge(ranked_graphs, unique_predicates, resolve_same=False, into=None):
    """Merge graphs into one, where later graphs take precedence.

    Args:
        ranked_graphs: named rdflib graphs from lowest to highest precedence.
        unique_predicates: predicates container that should implement
            `__contains__`.
        resolve_same: rename/update `owl:sameAs` IRIs.
        into: where to add merged triples. It should implement `add` method
            with a triple (s, p, o) argument. Defaults to a new `rdflib.Graph`.

    Returns:
        Tuple of the merged graph (or `into`) and a `ConflictReport`.

    For a unique predicate, the value from the highest ranked graph wins and
    the others are reported as dropped. Beside those, it is an union of graphs
    so a triple in several graphs appears once.
    """
    graphs = list(ranked_graphs)
    report = ConflictReport()
    merged = into
    if merged is None:
        merged = rdflib.Graph()
        _bind_namespaces(merged, graphs)

    aliases = _collect_aliases(graphs, report) if resolve_same else None
    is_unique = _unique_checker(unique_predicates)
    skip = OWL.sameAs if resolve_same else None

    kept = {}
    dropped_keyed = []
    conflicts_keyed = []
    # From highest rank down, so the first graph seen with a key wins
    for rank in reversed(range(len(graphs))):
        graph = graphs[rank].identifier
        by_key = _group_unique(
            graphs[rank], _renamer(aliases), is_unique, skip, merged)
        for key, objs in by_key.items():
            objs = _sorted_objs(objs) if isinstance(objs, set) else (objs,)
            winner = kept.get(key)
            if winner is None:
                winner = kept[key] = Kept(_choose(objs), graph)
                merged.add((*key, winner.obj))
            if len(objs) > 1:
                kept_here = winner.obj if winner.graph is graph else None
                conflicts_keyed.append(
                    (key, rank, SelfConflict(graph, *key, objs, kept_here)))
            if winner.graph is not graph:
                dropped_keyed.extend(
                    (key, rank, Dropped(*key, obj, graph, *winner))
                    for obj in objs if obj != winner.obj)

    report.dropped = _in_report_order(dropped_keyed)
    report.self_conflicts = _in_report_order(conflicts_keyed)
    return merged, report
