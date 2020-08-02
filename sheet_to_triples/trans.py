# Copyright 2020 Visual Meaning Ltd

"""Simple functional transformation implementation from rows to RDF.

The transform is specified in terms of one row at a time of tabular input with
reference to another graph for namespace mappings and lookup queries. Values
are template interpolated using a curly string syntax.

Using ``string.Formatter`` is not really ideal:

* Only outputs strings and we actually want ``rdflib.terms.Identifiers``
* Not actually safe for arbitrary input
* Ends up re-stringifying things more than necessary

But this is already too large for what was meant to be a simple experiment.
"""

import ast
import functools
import os
import re
import string

from rdflib.plugins import sparql

from . import (
    rdf,
)


def _as_iri(formatter, template, params):
    result = formatter.vformat(template, (), params)
    return rdf.from_qname(result)


def _as_obj(formatter, template, params):
    try:
        result = formatter.vformat(template, (), params)
    except (KeyError, ValueError):
        return None
    return rdf.from_identifier(result)


class Transform:
    """Class to load and process functional row to RDF transformation."""

    __slots__ = ('sheet', 'lets', 'queries', 'triples')

    def __init__(self, details):
        for k in details:
            setattr(self, k, details[k])

    @classmethod
    def from_name(cls, name):
        path = os.path.join('transforms', name + '.py')
        with open(path, 'r', encoding='utf-8') as f:
            return cls(ast.literal_eval(f.read()))

    def _fields(self):
        formatter = string.Formatter()
        lvars = set(v for v in self.lets.values())
        nodes = set(n for t in self.triples for n in t)
        strings = (s for s in nodes | lvars if '{' in s)
        return set(r[1] for n in strings for r in formatter.parse(n))

    def required_rows(self):
        pattern = re.compile(r'^row\[(.*?)\]')
        matches = (pattern.match(f) for f in self._fields())
        return set(m.group(1) for m in matches if m is not None)

    def prepare_queries(self, for_graph):
        f = for_graph.query
        ns = dict(for_graph.namespaces())
        return {
            k: functools.partial(f, sparql.prepareQuery(qs, initNs=ns))
            for k, qs in self.queries.items()}

    def process(self, reference_graph, row_iter):
        """Yield new tuples transformed from reference graph and rows.

        Currently row-at-a-time, which is mostly okay but prevents some
        possible cleverness to do with detecting duplicated rows or
        generated iris.
        """
        formatter = string.Formatter()
        queries = self.prepare_queries(reference_graph)

        for row in row_iter:
            yield from self._process_row(formatter, queries, row)

    def _process_row(self, _f, query_map, row):
        params = dict(query={}, row=row)
        for k in self.lets:
            params[k] = _as_obj(_f, self.lets[k], params)

        for k, q in query_map.items():
            result = list(q(initBindings=params))
            if result:
                [[params['query'][k]]] = result

        for s, p, o in self.triples:
            obj = _as_obj(_f, o, params)
            if obj is not None:
                yield (_as_iri(_f, s, params), _as_iri(_f, p, params), obj)
