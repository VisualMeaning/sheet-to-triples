# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Run group of transforms on existing data and graph."""

import json

from . import (
    field,
    rdf,
    xl,
)


class Runner:
    """Encapsulation of new data, existing model, and transform running."""

    def __init__(self, books, model, purge_except, verbose):
        self.books = books
        self.model = model
        if model:
            rdf.purge_terms(model, purge_except, verbose)
            self.graph = rdf.graph_from_model(model)
        else:
            self.graph = rdf.graph_from_triples(())
        self.verbose = verbose

    @classmethod
    def from_args(cls, args):
        book = args.book and list(map(xl.load, args.book))
        model = args.model and cls.load_model(args.model)
        return cls(book, model, args.purge_except, args.verbose)

    def run(self, transforms):
        for tf in transforms:
            triples = tf.process(self.graph, self._iter_data(tf))

            if self.verbose:
                triples = list(triples)
                show_graph(rdf.graph_from_triples(triples))

            # Note that model is updated but basis graph is not
            if self.model:
                rdf.update_model_terms(self.model, triples)

        if self.model:
            rdf.normalise_model(self.model, self.ns, self.verbose)

    @property
    def ns(self):
        return self.graph.namespace_manager

    def _iter_data(self, tf):
        if self.books and tf.uses_sheet():
            sheet = xl.find_sheet(self.books, tf.sheet)
            return xl.as_rows(sheet, tf.required_rows())
        return (field.Row(r) for r in getattr(tf, 'data', ()))

    @staticmethod
    def load_model(filepath):
        with open(filepath, 'rb') as f:
            return json.load(f)

    def save_model(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.model, f)


def show_graph(graph):
    """Print graph in human-readable turtle format."""
    print(graph.serialize(format='turtle').decode('utf-8'))
