# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Context specific RDF behaviours for Visual Meaning graphs."""

import functools
import json
import operator
import re

import rdflib.term


VM = rdflib.Namespace('http://visual-meaning.com/rdf/')
GRAPH = rdflib.Namespace('http://visual-meaning.com/rdf/graph/')
VMHE = VM['HE/']
_ISSUES_PREFIX = VM['issues/']
_USES_MAP_TILES = VM.usesMapTiles

_GEO = (VM.atGeoPoint.toPython(), VM.atGeoPoly.toPython(), VM.name.toPython())


class Resolver:
    #TODO: Make from_qname a method on this class. Will require rewriting
    # calling code in other modules.
    def __init__(self, store, namespaces):
        self.store = store
        self.ns_match = '|'.join(
            sorted(
                [re.escape(str(ns)) for _, ns in namespaces],
                key=len, reverse=True
            )
        )
        self.lang_match = re.compile(r"@[a-z]{2}$")

    @classmethod
    def from_graph(cls, graph):
        return cls(graph.store, graph.namespace_manager.namespaces())

    def from_identifier(self, value):
        if isinstance(value, rdflib.term.Identifier):
            return value
        prefix, _, tail = value.partition(':')
        if tail:
            namespace = self.store.namespace(prefix)
            if namespace:
                # Rough hack to see if this is a sequence path, and create
                if ' / ' in tail:
                    return functools.reduce(
                        operator.truediv, map(
                            lambda v: from_qname(v, self.store.namespace),
                            value.split(' / ')))
                return rdflib.URIRef(namespace + tail)
        if re.match(self.ns_match, value):
            return rdflib.URIRef(value)

        value = _norm(value)
        # if ends with language tag, create a Literal with the appropriate lang
        if re.search(self.lang_match, value):
            lang = value[-2:]
            value_without_lang = value[:-3]
            if value_without_lang.startswith('"') and value_without_lang.endswith('"'):
                inner = json.loads(value_without_lang)
            else:
                # {"k": "v"}@en compatibility
                inner = value_without_lang
            return rdflib.Literal(inner, lang=lang)
        return rdflib.Literal(value)


def _cast_from_term(t, from_identifier):
    return (
        rdflib.URIRef(t['subj']),
        rdflib.URIRef(t['pred']),
        from_identifier(t['obj']),
    )


def _norm(s, _w=re.compile(r'(?:(?<=\S)[^\S\n]+)')):
    return _w.sub(' ', s.replace('\r\n', '\n').replace('\u200b', ''))


def from_qname(qname, resolver):
    prefix, tail = qname.split(':', 1)
    namespace = resolver(prefix)
    if namespace:
        return rdflib.URIRef(namespace + tail)
    # TODO: Is this special casing for http: strictly needed now?
    if prefix == 'http':
        return rdflib.URIRef(qname)
    raise ValueError(f'unknown prefix: {prefix}')


def relates_geo_name(term):
    """`True` if triple is geo infomation or a name."""
    return term['pred'] in _GEO


def relates_issue(term):
    """`True` if triple is not related to an issue instance."""
    return not term['subj'].startswith(_ISSUES_PREFIX)


def purge_terms(model, retain, verbose):
    """Update model to only include terms that should be retained."""
    start_len = len(model['terms'])
    model['terms'] = [term for term in model['terms'] if retain(term)]
    for term in model['terms']:
        term['obj'] = _norm(term['obj'])
    if verbose:
        n_dropped = start_len - len(model['terms'])
        print(f'# not retained {n_dropped} terms')


def _bind_namespaces(graph):
    graph.bind('vm', VM)
    graph.bind('vmhe', VMHE)
    graph.bind('foaf', rdflib.namespace.FOAF)
    graph.bind('skos', rdflib.namespace.SKOS)
    graph.bind('owl', rdflib.namespace.OWL)
    graph.bind('gist', rdflib.Namespace('https://ontologies.semanticarts.com/gist/'))
    return graph


def _new_graph(identifier=None):
    return _bind_namespaces(rdflib.Graph(identifier=identifier))


def _new_dataset():
    return _bind_namespaces(rdflib.Dataset(default_union=True))


def _graph_in(dataset, identifier):
    if dataset is None:
        return _new_graph(identifier)
    return dataset.graph(identifier=identifier)


def graph_from_model(model, dataset=None, identifier=None):
    g = _graph_in(dataset, identifier)
    resolver = Resolver.from_graph(g)
    g.addN(
        _cast_from_term(term, resolver.from_identifier) + (g,)
        for term in model['terms'])
    return g


def _maybe_bnode(s, p, o):
    return isinstance(s, rdflib.term.BNode) or isinstance(o, rdflib.term.BNode)


def _maybe_from_literal(maybe_literal):
    """Serialise rdf object value to form used for model json encoding.

    There is a special case for when language tags are involved, to preserve
    them in the json serialisation for both strings and arrays or objects.
    """
    if getattr(maybe_literal, 'language', None):
        # For JSON arrays/objects, str() gives the JSON representation
        if maybe_literal[:1] + maybe_literal[-1:] in ('[]', '{}'):
            return str(maybe_literal) + '@' + maybe_literal.language
        # For regular strings, use json.dumps to properly escape
        # This ensures roundtrip compatibility with from_identifier
        return json.dumps(str(maybe_literal)) + '@' + maybe_literal.language
    return str(maybe_literal)


def update_model_terms(model, triples):
    model['terms'].extend(
        dict(subj=str(s), pred=str(p), obj=_maybe_from_literal(o))
        for s, p, o in triples
        if not _maybe_bnode(s, p, o))


def _with_int_maybe(iri):
    try:
        prefix, maybe_int = iri.rsplit('/', 1)
        return (prefix, maybe_int)
    except ValueError:
        return (iri,)


def functional_properties(graph):
    return set(graph.subjects(
        rdflib.namespace.RDF.type, rdflib.namespace.OWL.FunctionalProperty))


def terms_from_triples(triples):
    """Serialise graph or triples as model terms, in an order:
    vm:asOrdinal of the subject, then subject, predicate and object.

    Triples with blank nodes are left out, as terms cannot express them.
    """
    terms = {
        (str(s), str(p), _maybe_from_literal(o))
        for s, p, o in triples
        if not _maybe_bnode(s, p, o)
    }

    order_pred = VM.asOrdinal.toPython()
    no_order = float('Inf')
    ordinals = {}
    for subj, pred, obj in terms:
        if pred == order_pred:
            ordinals[subj] = min(float(obj), ordinals.get(subj, no_order))

    def term_sort_key(term):
        return (
            ordinals.get(term[0], no_order),
            _with_int_maybe(term[0]),
            term[1],
            term[2],
        )

    return [
        dict(subj=s, pred=p, obj=o)
        for s, p, o in sorted(terms, key=term_sort_key)
    ]


def graph_from_triples(triples, dataset=None, identifier=None):
    g = _graph_in(dataset, identifier)
    for triple in triples:
        g.add(triple)
    return g
