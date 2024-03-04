# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

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
import itertools
import os
import re
import string

from rdflib.plugins import sparql

from . import (
    rdf,
    field,
)


class _Converter:
    """Class to interpret transform value fields as graph identifiers."""

    def __init__(self, reference_graph):
        self.vformat = string.Formatter().vformat
        # TODO: Integrate from_qname into new Resolver class and remove this
        self._old_resolver = reference_graph.store.namespace
        self.resolver = rdf.Resolver.from_graph(reference_graph)

    def as_iri(self, template, params):
        result = self.vformat(template, (), params)
        return rdf.from_qname(result, self._old_resolver)

    def as_iri_or_none(self, template, params):
        try:
            result = self.vformat(template, (), params)
        except (IndexError, KeyError, ValueError):
            return None
        if not result:
            # TODO: Raise in this case, partial rows are problems here
            return None
        return rdf.from_qname(result, self._old_resolver)

    def as_obj(self, template, params):
        try:
            result = self.vformat(template, (), params)
        except (IndexError, KeyError, ValueError):
            return None
        return self.resolver.from_identifier(result)


class Transform:
    """Class to load and process functional row to RDF transformation."""

    __slots__ = (
        'name',
        'data',
        'book',
        'sheet',
        'lets',
        'conds',
        'queries',
        'triples',
        'non_unique',
        'allow_empty_subject',
        'skip_empty_rows',
        'melt_cols',
        'sheet_encoding',
    )

    def __init__(self, name, details):
        self.name = name
        self.book = None
        self.skip_empty_rows = False
        self.lets = dict()
        self.conds = dict()
        self.triples = []
        self.melt_cols = ()
        self.sheet_encoding = 'utf-8'
        for k in details:
            setattr(self, k, details[k])

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name!r}>'

    @classmethod
    def iter_from_name(cls, name, base_path=None):
        if base_path is None:
            base_path = os.getenv('TRANSFORMS_DIR', 'transforms')
        path = os.path.join(base_path, name)
        if not path.endswith('.py'):
            path += '.py'

        with open(path, 'r', encoding='utf-8') as f:
            transform = ast.literal_eval(f.read())
            if isinstance(transform, list):
                for t in transform:
                    yield cls(name, t)
            else:
                yield cls(name, transform)

    def get_non_uniques(self, namespace_manager):
        non_unique = getattr(self, 'non_unique', ())
        resolver = namespace_manager.store.namespace
        # would we ever want to template this and use as_iri instead?
        return set(rdf.from_qname(q, resolver).toPython() for q in non_unique)

    def uses_sheet(self):
        return hasattr(self, 'sheet')

    def _fields(self):
        formatter = string.Formatter()
        lvars = set(v for v in self.lets.values())
        nodes = set(n for t in self.triples for n in t)
        condvars = set(
            itertools.chain.from_iterable(c for c in self.conds.values())
        )
        strings = (s for s in nodes | lvars | condvars if '{' in s)
        return set(r[1] for n in strings for r in formatter.parse(n))

    def required_cols(self):
        pattern = re.compile(r'^row\[(.*?)\]')
        matches = (pattern.match(f) for f in self._fields() if f is not None)
        cols_used = set(
            m.group(1) for m in matches if m is not None
            # columns with underscores are internally set after data ingestion
            and not m.group(1).startswith('_')
        )
        cols_used.update(self.melt_cols)
        return cols_used

    def prepare_queries(self, for_graph):
        if not getattr(self, 'queries', None):
            return {}
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
        converter = _Converter(reference_graph)
        queries = self.prepare_queries(reference_graph)

        for n, row in enumerate(row_iter, 1):
            yield from self._process_row(converter, queries, row, n)

    def _generate_params(self, converter, query_map, row, n):
        params = dict(query={}, row=row, n=n)

        def _convert(template):
            return converter.as_obj(template, params)

        for k in self.lets:
            # TODO: Defaulting to empty string is wrong if variable can't bind
            params[k] = _convert(self.lets[k]) or ''

        for c in self.conds:
            cond, true, false = self.conds[c]
            if all([str(_convert(c.strip())) == "True" for c in cond.split('&')]):
                params[c] = _convert(true)
            else:
                params[c] = _convert(false)

        for k, q in query_map.items():
            result = list(q(initBindings=params))
            if result:
                [[params[k]]] = result

        return params

    def _process_row(self, converter, query_map, row, n):
        iter_row = self._iter_row_triples

        # if it's fed in directly from the transform data field,
        # convert to Row for access to Row methods
        if isinstance(row, dict):
            row = field.Row(row)

        if self.melt_cols:
            for row in row.melt(self.melt_cols):
                params = self._generate_params(converter, query_map, row, n)
                yield from iter_row(converter, params)
        else:
            params = self._generate_params(converter, query_map, row, n)
            yield from iter_row(converter, params)

    @property
    def _iter_row_triples(self):
        if getattr(self, 'allow_empty_subject', False):
            return self._iter_row_triples_some_subj
        return self._iter_row_triples_must_subj

    def _iter_row_triples_must_subj(self, _c, params):
        for s, p, o in self.triples:
            obj = _c.as_obj(o, params)
            if obj is not None:
                yield (_c.as_iri(s, params), _c.as_iri(p, params), obj)

    def _iter_row_triples_some_subj(self, _c, params):
        for s, p, o in self.triples:
            obj = _c.as_obj(o, params)
            if obj is not None:
                subj = _c.as_iri_or_none(s, params)
                if subj is not None:
                    yield (subj, _c.as_iri(p, params), obj)
