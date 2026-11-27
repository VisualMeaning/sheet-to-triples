# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Run group of transforms on existing data and graph."""

import json
import os
import urllib.parse

import rdflib

from . import (
    field,
    merge,
    rdf,
    xl,
)

default_model = object()

# TODO: this should not hardcode RDF namespaces
# TODO: move this somewhere more appropriate
_default_non_unique = {
    'http://visual-meaning.com/rdf/classOfInterest',
    'http://visual-meaning.com/rdf/useFilters',
}


def _graph_name(name):
    """Short name of a graph's source for its identifier.

    Plain names and relative paths are kept, but absolute paths and those
    outside the working directory are cut to the file name, so identifiers
    don't carry a whole filesystem location. Rank keeps identifiers unique.
    """
    path = os.path.normpath(name)
    if os.path.isabs(path) or path.split(os.sep)[0] == os.pardir:
        path = os.path.basename(path)
    return path.replace(os.sep, '/')


def graph_identifier(kind, rank, name=None):
    parts = [kind, str(rank)]
    if name:
        parts.append(_graph_name(name))
    return rdf.GRAPH[urllib.parse.quote('/'.join(parts), safe='/@')]


def graph_label(identifier):
    value = str(identifier)
    if value.startswith(rdf.GRAPH):
        return urllib.parse.unquote(value[len(rdf.GRAPH):])
    return value


class Runner:
    """Encapsulation of new data, existing model, and transform running.

    Every input and transform output is kept as its own named graph in
    `dataset`, ranked by precedence in `graphs`:
      1. input model, after clean up
      2. each added graph, in the order added
      3. each transform's output, in run order
    """

    def __init__(
        self,
        books,
        model,
        purge_except,
        resolve_same,
        use_ontology_normalisation,
        drop_duplicates,
        verbose,
        non_unique=None,
        model_name=None,
    ):
        self.books = books
        self.model = model
        self.dataset = rdf._new_dataset()
        self.graphs = []
        if model:
            rdf.purge_terms(model, purge_except, verbose)
            graph = self._new_ranked_graph('model', model_name)
            rdf.graph_from_model(
                model, dataset=self.dataset, identifier=graph.identifier)
        self.normalisation_params = {
            'non_uniques': _default_non_unique.copy() if non_unique is None \
                           else non_unique,
            'from_ontology': use_ontology_normalisation,
            'drop_duplicates': drop_duplicates,
            'resolve_same': resolve_same
        }
        self.verbose = verbose

    @classmethod
    def from_args(cls, args):
        if args.book:
            book = {os.path.basename(b): xl.load_book(b) for b in args.book
                    if xl.is_an_actual_file(b)}
        else:
            book = dict()
        model = args.model and cls.load_model(args.model)
        model_name = args.model if isinstance(args.model, str) else None
        return cls(
            book,
            model,
            args.purge_except,
            args.resolve_same,
            args.use_ontology_normalisation,
            args.drop_duplicates,
            args.verbose,
            model_name=model_name,
        )

    @property
    def graph(self):
        """Graph transforms read from, the union of graphs in the dataset.

        By default transform outputs only join the dataset after all have
        run, so this is the existing model plus any added graphs.
        """
        return self.dataset

    @property
    def ns(self):
        return self.dataset.namespace_manager

    def _new_ranked_graph(self, kind, name=None):
        identifier = graph_identifier(kind, len(self.graphs), name)
        # always creates
        graph = self.dataset.graph(identifier=identifier)
        self.graphs.append(graph)
        return graph

    def add_graph(self, path, format='ttl'):
        graph = self._new_ranked_graph('add-graph', path)
        graph.parse(path, format=format)
        return graph

    def add_triples_graph(self, kind, name, triples):
        """Add triples collection as a new graph."""
        graph = self._new_ranked_graph(kind, name)
        graph.addN((s, p, o, graph) for s, p, o in triples)
        return graph

    def use_non_uniques(self, old_transforms):
        for tf in old_transforms:
            self.normalisation_params['non_uniques'].update(
                tf.get_non_uniques(self.ns))

    def run(self, transforms):
        deferred = []
        for tf in transforms:
            triples = list(tf.process(self.graph, self._iter_data(tf)))
            self.normalisation_params['non_uniques'].update(
                tf.get_non_uniques(self.ns))

            if self.verbose:
                show_graph(rdf.graph_from_triples(triples))

            deferred.append((tf.name, triples))

        for name, triples in deferred:
            self.add_triples_graph('transform', name, triples)

        if self.model:
            merged, report = self.merge(into=TripleList())
            self.show_report(report)
            self.model['terms'] = rdf.terms_from_triples(merged)

    def unique_predicates(self):
        if self.normalisation_params['from_ontology']:
            return merge.UniquePredicates.only(
                rdf.functional_properties(self.dataset))
        return merge.UniquePredicates.all_except(
            self.normalisation_params['non_uniques'])

    def merge(self, into=None):
        """Merge graphs into a single graph with a conflict report."""
        ranked = self.graphs
        if self.normalisation_params['drop_duplicates'] == 'keep-oldest':
            ranked = ranked[::-1]
        return merge.merge(
            ranked,
            self.unique_predicates(),
            resolve_same=self.normalisation_params['resolve_same'],
            into=into,
        )

    def show_report(self, report):
        ns = self.ns
        if self.verbose:
            for alias in report.aliases:
                print('# aliasing {o} => {s}'.format(
                    s=_n3(alias.canonical, ns), o=_n3(alias.alias, ns)))

        for conflict in report.self_conflicts:
            print('# warning: {g} has several values for {s} {p}'.format(
                g=graph_label(conflict.graph),
                s=_n3(conflict.subject, ns),
                p=_n3(conflict.predicate, ns),
            ))
            for obj in conflict.objs:
                kept = ' (kept)' if obj == conflict.kept else ''
                print(f'#   {_obj_for_print(obj)}{kept}')

        for drop in report.dropped:
            if not (self.verbose or _differ(drop.obj, drop.kept_obj)):
                continue
            print('# dropped {s} {p} {o}'.format(
                s=_n3(drop.subject, ns),
                p=_n3(drop.predicate, ns),
                o=_obj_for_print(drop.obj),
            ))
            print('#   from {g}, kept from {k}: {o}'.format(
                g=graph_label(drop.graph),
                k=graph_label(drop.kept_graph),
                o=_obj_for_print(drop.kept_obj),
            ))

    def _get_books(self, book):
        if book:
            if book not in self.books:
                raise ValueError('required book {} not found'.format(book))
            return [self.books[book]]
        return self.books.values()

    def _iter_data(self, tf):
        if self.books and tf.uses_sheet():
            row_iter = xl.iter_sheet(
                self._get_books(tf.book), tf.sheet, tf.sheet_encoding)
            return xl.as_rows(
                row_iter, tf.required_cols(), tf.skip_empty_rows)
        return (field.Row(r) for r in getattr(tf, 'data', ()))

    @staticmethod
    def load_model(filepath):
        if filepath is default_model:
            return {'terms': []}
        with open(filepath, 'rb') as f:
            model = json.load(f)
        if isinstance(model, dict) and 'terms' in model:
            return model
        if isinstance(model, list) and all(isinstance(t, dict) for t in model):
            return {'terms': model}
        raise ValueError('invalid model: ' + filepath)

    def save_model(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.model, f, ensure_ascii=False)


class TripleList(list):
    add = list.append


def _n3(term, namespace_manager):
    return rdflib.URIRef(str(term)).n3(namespace_manager)


def _obj_for_print(obj):
    """Comment out all lines of newline separated string."""
    if not isinstance(obj, rdflib.Literal):
        return obj
    return '\n#  '.join(str(obj).splitlines())


def _differ(a, b):
    return rdf._maybe_from_literal(a) != rdf._maybe_from_literal(b)


def show_graph(graph):
    """Print graph in human-readable turtle format."""
    print(graph.serialize(format='turtle'))
