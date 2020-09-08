# Copyright 2020 Visual Meaning Ltd

"""Context specific RDF behaviours for Visual Meaning graphs."""

import functools
import operator

import rdflib.term


VM = rdflib.Namespace('http://visual-meaning.com/rdf/')
_ISSUES_PREFIX = VM['issues/']
_USES_MAP_TILES = VM.usesMapTiles


def _cast_from_term(t):
    return (
        rdflib.URIRef(t['subj']),
        rdflib.URIRef(t['pred']),
        from_identifier(t['obj']),
    )


def from_qname(qname, namespaces=rdflib.namespace):
    if qname.startswith('vm:'):
        return VM[qname[3:]]
    if qname.startswith('http:'):
        return rdflib.URIRef(qname)
    prefix, last = qname.split(':', 1)
    return getattr(namespaces, prefix.upper())[last]


def from_identifier(value, prefixes=('vm:', 'rdf:')):
    if isinstance(value, rdflib.term.Identifier):
        return value
    if value.startswith(prefixes):
        # This is something of a hack, but detecting property paths seems
        # difficult due to syntax overlap, will have to be explicit instead.
        if ' / ' in value:
            return functools.reduce(
                operator.truediv, map(from_qname, value.split(' / ')))
        return from_qname(value)
    if value.startswith('http:'):
        return rdflib.URIRef(value)
    return rdflib.Literal(value)


def _should_retain(term):
    """Keep triple in graph for querying and update."""
    return not (
        term['subj'].startswith(_ISSUES_PREFIX) or
        term['pred'] == _USES_MAP_TILES.toPython())


def purge_terms(model):
    """Update model to only include terms that are not issues."""
    model['terms'] = [term for term in model['terms'] if _should_retain(term)]


def graph_from_model(model):
    g = rdflib.Graph(base=VM)
    g.bind('vm', VM)
    for term in model['terms']:
        g.add(_cast_from_term(term))
    return g


def update_model_terms(model, triples):
    model['terms'].extend(dict(subj=s, pred=p, obj=o) for s, p, o in triples)


eco_silly = {
    '10': 8.5,
    '15': 12.5,
    '16': 0.5,
}


def _with_int_maybe(iri):
    try:
        prefix, maybe_int = iri.rsplit('/', 1)
        return (prefix, eco_silly.get(maybe_int, int(maybe_int)))
    except ValueError:
        return (iri,)


def normalise_model(model):
    model['terms'].sort(key=lambda t: (_with_int_maybe(t['subj']), t['pred']))
    # TODO: Could also validate constraints here, like no duplicates


def graph_from_triples(triples):
    g = rdflib.Graph(base=VM)
    g.bind('vm', VM)
    for triple in triples:
        g.add(triple)
    return g
