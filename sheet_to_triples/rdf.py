# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Context specific RDF behaviours for Visual Meaning graphs."""

import functools
import operator
import re

import rdflib.term


VM = rdflib.Namespace('http://visual-meaning.com/rdf/')
VMHE = VM['HE/']
_ISSUES_PREFIX = VM['issues/']
_USES_MAP_TILES = VM.usesMapTiles

_GEO = (VM.atGeoPoint.toPython(), VM.atGeoPoly.toPython(), VM.name.toPython())

FOAF = rdflib.namespace.FOAF
# Include test property via hack <http://xmlns.com/foaf/spec/#term_phone>
FOAF._ClosedNamespace__uris['phone'] = rdflib.URIRef(FOAF.uri + 'phone')


def _cast_from_term(t):
    return (
        rdflib.URIRef(t['subj']),
        rdflib.URIRef(t['pred']),
        from_identifier(t['obj'], None),
    )


def _norm(s, _w=re.compile(r'(?:(?!\n)\s)+')):
    return _w.sub(' ', s.replace('\u200b', ''))


def _n3(uri, namespace_manager):
    return rdflib.URIRef(uri).n3(namespace_manager)


def from_qname(qname, resolver):
    prefix, tail = qname.split(':', 1)
    namespace = resolver(prefix)
    if namespace:
        return rdflib.URIRef(namespace + tail)
    # TODO: Is this special casing for http: strictly needed now?
    if prefix == 'http':
        return rdflib.URIRef(qname)
    raise ValueError(f'unknown prefix: {prefix}')


def from_identifier(value, resolver):
    if isinstance(value, rdflib.term.Identifier):
        return value
    prefix, _, tail = value.partition(':')
    if tail and resolver:
        # This is something of a hack, but detecting property paths seems
        # difficult due to syntax overlap, will have to be explicit instead.
        if ' / ' in value:
            return functools.reduce(
                operator.truediv, map(
                    lambda v: from_qname(v, resolver),
                    value.split(' / ')))
        namespace = resolver(prefix)
        if namespace:
            return rdflib.URIRef(namespace + tail)
    if prefix == 'http':
        return rdflib.URIRef(value)
    return rdflib.Literal(value)


def relates_geo_name(term):
    """True if triple is geo infomation or a name."""
    return term['pred'] in _GEO


def relates_issue(term):
    """True if triple is not related to an issue instance."""
    return not term['subj'].startswith(_ISSUES_PREFIX)


def purge_terms(model, retain, verbose):
    """Update model to only include terms that are not issues."""
    start_len = len(model['terms'])
    model['terms'] = [term for term in model['terms'] if retain(term)]
    for term in model['terms']:
        term['obj'] = _norm(term['obj'])
    if verbose:
        n_dropped = start_len - len(model['terms'])
        print(f'# dropped {n_dropped} terms')


def _new_graph():
    g = rdflib.Graph()
    g.bind('vm', VM)
    g.bind('vmhe', VMHE)
    g.bind('foaf', rdflib.namespace.FOAF)
    g.bind('skos', rdflib.namespace.SKOS)
    g.bind('owl', rdflib.namespace.OWL)
    return g


def graph_from_model(model):
    g = _new_graph()
    for term in model['terms']:
        g.add(_cast_from_term(term))
    return g


def update_model_terms(model, triples):
    model['terms'].extend(
        dict(subj=str(s), pred=str(p), obj=str(o)) for s, p, o in triples)


def _with_int_maybe(iri):
    try:
        prefix, maybe_int = iri.rsplit('/', 1)
        return (prefix, maybe_int)
    except ValueError:
        return (iri,)


def _to_key(t, non_uniques):
    if t['pred'] in non_uniques:
        return t['subj'], t['pred'], t['obj']
    return t['subj'], t['pred']


def normalise_model(model, ns, non_uniques, resolve_same, verbose):
    terms = model['terms']
    # Record subjects that have been renamed so triples can be moved over
    same = {}
    if resolve_same:
        sameAs = rdflib.namespace.OWL.sameAs.toPython()
        for i in reversed(range(len(terms))):
            t = terms[i]
            if t['pred'] == sameAs:
                same[t['obj']] = t['subj']
                if verbose:
                    print('# aliasing {o} => {s}'.format(
                        s=_n3(t['subj'], ns), o=_n3(t['obj'], ns)))
                del terms[i]

    # While multiple objects for a subject, predicate are generally fine
    # Our model asserts uniqueness, so discard older values.
    by_key = {}
    for t in terms:
        for k in ('subj', 'pred', 'obj'):
            if t[k] in same:
                t[k] = same[t[k]]
        key = _to_key(t, non_uniques)
        if verbose and key in by_key:
            print('# dropping {s} {p} {o}'.format(
                s=_n3(key[0], ns), p=_n3(key[1], ns), o=by_key[key]['obj']))
        by_key[key] = t

    order_pred = VM.asOrdinal.toPython()
    no_order = {'obj': 'Inf'}

    def term_sort_key(term):
        """Sort key for term, closed over by_key term index."""
        return (
            float(by_key.get((term['subj'], order_pred), no_order)['obj']),
            _with_int_maybe(term['subj']),
            term['pred'],
        )

    # Produce stable output order for terms (with some extra hacks)
    model['terms'] = sorted(by_key.values(), key=term_sort_key)


def graph_from_triples(triples):
    g = _new_graph()
    for triple in triples:
        g.add(triple)
    return g
