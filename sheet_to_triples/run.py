# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Run group of transforms on existing data and graph."""

import json
import os

from . import (
    field,
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


class Runner:
    """Encapsulation of new data, existing model, and transform running."""

    def __init__(
        self,
        books,
        model,
        purge_except,
        resolve_same,
        verbose,
        non_unique=None
    ):
        self.books = books
        self.model = model
        if model:
            rdf.purge_terms(model, purge_except, verbose)
            self.graph = rdf.graph_from_model(model)
        else:
            self.graph = rdf.graph_from_triples(())
        self.non_unique = non_unique
        if self.non_unique is None:
            self.non_unique = _default_non_unique
        self.resolve_same = resolve_same
        self.verbose = verbose

    @classmethod
    def from_args(cls, args):
        if args.book:
            book = {os.path.basename(b): xl.load_book(b) for b in args.book}
        else:
            book = dict()
        # if args.model == 'default':
        #     model = {'terms': []}
        # else:
        model = args.model and cls.load_model(args.model)
        return cls(
            book, model, args.purge_except, args.resolve_same, args.verbose)

    def use_non_uniques(self, old_transforms):
        for tf in old_transforms:
            self.non_unique.update(tf.get_non_uniques(self.ns))

    def set_terms(self, triples):
        if self.model:
            self.model['terms'][:] = ()
            rdf.update_model_terms(self.model, sorted(triples))

    def run(self, transforms):
        for tf in transforms:
            triples = tf.process(self.graph, self._iter_data(tf))
            self.non_unique.update(tf.get_non_uniques(self.ns))

            if self.verbose:
                triples = list(triples)
                show_graph(rdf.graph_from_triples(triples))

            # Note that model is updated but basis graph is not
            if self.model:
                rdf.update_model_terms(self.model, triples)

        if self.model:
            rdf.normalise_model(
                self.model, self.ns, self.non_unique, self.resolve_same,
                self.verbose)

    @property
    def ns(self):
        return self.graph.namespace_manager

    def _get_books(self, book):
        if book:
            if book not in self.books:
                raise ValueError('required book {} not found'.format(book))
            return [self.books[book]]
        return self.books.values()

    def _iter_data(self, tf):
        if self.books and tf.uses_sheet():
            row_iter = xl.iter_sheet(self._get_books(tf.book), tf.sheet)
            return xl.as_rows(
                row_iter, tf.required_cols(), tf.skip_empty_rows)
        return (field.Row(r) for r in getattr(tf, 'data', ()))

    @staticmethod
    def load_model(filepath):
        if filepath is default_model:
            return {'terms': []}
        with open(filepath, 'rb') as f:
            return json.load(f)

    def save_model(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.model, f, ensure_ascii=False)


def show_graph(graph):
    """Print graph in human-readable turtle format."""
    print(graph.serialize(format='turtle'))
