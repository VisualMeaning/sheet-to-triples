# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Context specific RDF behaviours for Visual Meaning graphs."""

import functools
import operator
import re

import rdflib.term


VM = rdflib.Namespace('http://visual-meaning.com/rdf/')
VMHE = VM['HE/']
PREFIX2NAMESPACE = {
    # namespaces already included elsewhere in VM code,
    # but that could be directly imported using rdfLib instead
    'dc'            : 'http://purl.org/dc/elements/1.1/',
    'dcat'          : 'http://www.w3.org/ns/dcat/',
    'dct'           : 'http://purl.org/dc/terms/',
    'dcterms'       : 'http://purl.org/dc/terms/',
    'org'           : 'http://www.w3.org/ns/org/',
    'rdf'           : 'http://www.w3.org/1999/02/22-rdf-syntax-ns/',
    'rdfs'          : 'http://www.w3.org/2000/01/rdf-schema/',
    'skos'          : 'http://www.w3.org/2004/02/skos/core/',
    # custom defined rdflib namespaces
    'gist'          : 'https://ontologies.semanticarts.com/gist/',
    'oa'            : 'http://www.w3.org/ns/oa/',
    'webprotege'    : 'http://webprotege.stanford.edu/',
    # custom defined rdflib namespaces for eu project
    'adms'          : 'http://www.w3.org/ns/adms/',
    'adms1'         : 'http://purl.org/adms/',
    'dg'            : 'https://w3id.org/dingo/',
    'eccf'          : 'http://data.europa.eu/54i/',
    'eubud'         : 'http://data.europa.eu/3rx/ontology/budget/',
    'eurio'         : 'http://data.europa.eu/s66/',
    'fabio'         : 'http://purl.org/spar/fabio/',
    'frapo'         : 'http://purl.org/cerif/frapo/',
    'locn'          : 'http://www.w3.org/ns/locn/',
    'patent'        : 'http://data.epo.org/linked-data/def/patent/',
    'schema'        : 'http://schema.org/',
    'turtle'        : 'http://www.semanticweb.org/owl/owlapi/turtle/',
    'xml'           : 'http://www.w3.org/XML/1998/namespace',
}

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
            inner = value[1:-4] if value[0] == '"' else value[:-3]
            return rdflib.Literal(inner, lang=value[-2:])
        return rdflib.Literal(value)


def _cast_from_term(t, from_identifier):
    return (
        rdflib.URIRef(t['subj']),
        rdflib.URIRef(t['pred']),
        from_identifier(t['obj']),
    )


def _norm(s, _w=re.compile(r'(?:(?<=\S)[^\S\n]+)')):
    return _w.sub(' ', s.replace('\r\n', '\n').replace('\u200b', ''))


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


def _new_graph():
    g = rdflib.Graph()
    g.bind('vm', VM)
    g.bind('vmhe', VMHE)

    # rdflib namespaces available for direct import
    g.bind('brick', rdflib.namespace.BRICK)
    g.bind('csvw', rdflib.namespace.CSVW)
    g.bind('dcmitype', rdflib.namespace.DCMITYPE)
    g.bind('dcam', rdflib.namespace.DCAM)
    g.bind('doap', rdflib.namespace.DOAP)
    g.bind('foaf', rdflib.namespace.FOAF)
    g.bind('odrl2', rdflib.namespace.ODRL2)
    g.bind('owl', rdflib.namespace.OWL)
    g.bind('prof', rdflib.namespace.PROF)
    g.bind('prov', rdflib.namespace.PROV)
    g.bind('qb', rdflib.namespace.QB)
    g.bind('sdo', rdflib.namespace.SDO)
    g.bind('sh', rdflib.namespace.SH)
    g.bind('sosa', rdflib.namespace.SOSA)
    g.bind('ssn', rdflib.namespace.SSN)
    g.bind('time', rdflib.namespace.TIME)
    g.bind('vann', rdflib.namespace.VANN)
    g.bind('void', rdflib.namespace.VOID)
    g.bind('wgs', rdflib.namespace.WGS)
    g.bind('xsd', rdflib.namespace.XSD)

    for prefix, namespace in PREFIX2NAMESPACE.items():
        g.bind(prefix, rdflib.Namespace(namespace))
    return g


def graph_from_model(model):
    g = _new_graph()
    resolver = Resolver.from_graph(g)
    for term in model['terms']:
        g.add(_cast_from_term(term, resolver.from_identifier))
    return g


def _maybe_bnode(s, p, o):
    return isinstance(s, rdflib.term.BNode) or isinstance(o, rdflib.term.BNode)


def _maybe_from_literal(maybe_literal):
    """Serialise rdf object value to form used for model json encoding.

    There is a special case for when language tags are involved, to preserve
    them in the json serialisation for both strings and arrays or objects.
    """
    if getattr(maybe_literal, 'language', None):
        if maybe_literal[:1] + maybe_literal[-1:] in ('[]', '{}'):
            return str(maybe_literal) + '@' + maybe_literal.language
        return maybe_literal.n3()
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


def _to_key(t, predicates, from_ontology):
    if (not from_ontology and t['pred'] in predicates) or \
        (from_ontology and t['pred'] not in predicates):
        return t['subj'], t['pred'], t['obj']
    return t['subj'], t['pred']


def _obj_for_print(obj):
    """Comment out all lines of newline separated string."""
    if not isinstance(obj, rdflib.Literal):
        return obj
    return '\n#  '.join(str(obj).splitlines())


def _functional_properties(model):
    owl = rdflib.namespace.OWL
    rdf = rdflib.namespace.RDF
    uniques = set()
    # going through whole model again to do this is expensive
    for t in model['terms']:
        if t['pred'] == str(rdf['type']) and t['obj'] == str(owl['FunctionalProperty']):
            uniques.add(t['subj'])
    return uniques


def normalise_model(model, ns, norm_params, verbose):
    terms = model['terms']
    # Record subjects that have been renamed so triples can be moved over
    same = {}
    if norm_params['resolve_same']:
        sameAs = rdflib.namespace.OWL.sameAs.toPython()
        for i in reversed(range(len(terms))):
            t = terms[i]
            if t['pred'] == sameAs:
                same[t['obj']] = t['subj']
                if verbose:
                    print('# aliasing {o} => {s}'.format(
                        s=_n3(t['subj'], ns), o=_n3(t['obj'], ns)))
                del terms[i]

    from_onto = norm_params['from_ontology']
    norm_preds = norm_params['non_uniques'] if not from_onto \
                 else _functional_properties(model)

    # While multiple objects for a subject, predicate are generally fine
    # Our model asserts uniqueness, so discard older values.
    by_key = {}
    iter_terms = reversed(terms) if norm_params['drop_duplicates'] == 'keep-oldest' \
                 else terms
    for t in iter_terms:
        for k in ('subj', 'pred', 'obj'):
            if t[k] in same:
                t[k] = same[t[k]]
        key = _to_key(t, norm_preds, from_onto)
        if key in by_key and (verbose or by_key[key]['obj'] != t['obj']):
            print('# dropping {s} {p} {o}'.format(
                s=_n3(key[0], ns),
                p=_n3(key[1], ns),
                o=_obj_for_print(by_key[key]['obj'])
            ))
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
