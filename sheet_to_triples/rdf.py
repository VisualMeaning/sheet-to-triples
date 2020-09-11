# Copyright 2020 Visual Meaning Ltd

"""Context specific RDF behaviours for Visual Meaning graphs."""

import functools
import operator
import re

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


def _norm(s, _w=re.compile(r'(?:(?!\n)\s)+')):
    return _w.sub(' ', s.replace('\u200b', ''))


def _n3(uri, namespace_manager):
    return rdflib.URIRef(uri).n3(namespace_manager)


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


def purge_terms(model, verbose):
    """Update model to only include terms that are not issues."""
    start_len = len(model['terms'])
    model['terms'] = [term for term in model['terms'] if _should_retain(term)]
    for term in model['terms']:
        term['obj'] = _norm(term['obj'])
    if verbose:
        n_dropped = start_len - len(model['terms'])
        print(f'# dropped {n_dropped} terms')


def graph_from_model(model):
    g = rdflib.Graph(base=VM)
    g.bind('vm', VM)
    for term in model['terms']:
        g.add(_cast_from_term(term))
    return g


def update_model_terms(model, triples):
    model['terms'].extend(
        dict(subj=str(s), pred=str(p), obj=str(o)) for s, p, o in triples)


eco_silly = {
    '10': 8.5,
    '15': 12.5,
    '16': 0.5,
    '17': 13,
}


def _with_int_maybe(iri):
    try:
        prefix, maybe_int = iri.rsplit('/', 1)
        return (prefix, eco_silly.get(maybe_int, int(maybe_int)))
    except ValueError:
        return (iri,)


def term_sort_key(term):
    return _with_int_maybe(term['subj']), term['pred']


def normalise_model(model, ns, verbose):
    # While multiple objects for a subject, predicate are generally fine
    # Our model asserts uniqueness, so discard older values.
    by_key = {}
    for t in model['terms']:
        key = (t['subj'], t['pred'])
        if verbose and key in by_key:
            print('# dropping {s} {p} {o}'.format(
                s=_n3(key[0], ns), p=_n3(key[1], ns), o=by_key[key]['obj']))
        by_key[key] = t

    # Produce stable output order for terms (with some extra hacks)
    model['terms'] = sorted(by_key.values(), key=term_sort_key)


def graph_from_triples(triples):
    g = rdflib.Graph(base=VM)
    g.bind('vm', VM)
    for triple in triples:
        g.add(triple)
    return g
