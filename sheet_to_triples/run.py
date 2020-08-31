# Copyright 2020 Visual Meaning Ltd

"""Run group of transforms on existing data and graph."""

import json

from . import (
    field,
    rdf,
    trans,
    xl,
)


class Runner:
    """Encapsulation of new data, existing model, and transform running."""

    def __init__(self, book, model, verbose):
        self.book = book
        self.model = model
        self.graph = (
            rdf.graph_from_model(model) if model else
            rdf.graph_from_triples(()))
        self.verbose = verbose

    @classmethod
    def from_args(cls, args):
        book = args.book and xl.load(args.book)
        graph = args.model and cls.load_model(args.model)
        return cls(book, graph, args.verbose)

    def run(self, transforms):
        for name in transforms:
            tf = trans.Transform.from_name(name)
            triples = tf.process(self.graph, self._iter_data(tf))

            if self.verbose:
                triples = list(triples)
                show_graph(rdf.graph_from_triples(triples))

            # Note that model is updated but basis graph is not
            if self.model:
                rdf.update_model_terms(self.model, triples)

    def _iter_data(self, tf):
        if tf.sheet:
            if not self.book:
                raise ValueError(f'book must be supplied for {tf}')
            sheet = xl.sheet(self.book, tf.sheet)
            return xl.as_rows(sheet, tf.required_rows())
        return (field.Row(r) for r in getattr(tf, 'data', ()))

    @staticmethod
    def load_model(filepath):
        with open(filepath, 'rb') as f:
            model = json.load(f)
        # TODO: Unconditional purging is wrong
        rdf.purge_terms(model)
        return model

    def save_model(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.model, f)


def show_graph(graph):
    """Print graph in human-readable turtle format."""
    print(graph.serialize(format='turtle').decode('utf-8'))
