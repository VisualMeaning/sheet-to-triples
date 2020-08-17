# Copyright 2020 Visual Meaning Ltd

"""Convert tabular data into triples."""

import argparse
import json
import sys

from . import (
    rdf,
    trans,
    xl,
)


def main(argv):
    parser = argparse.ArgumentParser(argv[0], description=__doc__)
    parser.add_argument('--book', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--model-out', metavar='PATH', default='new.json')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('transform', nargs='+')
    args = parser.parse_args(argv[1:])

    with open(args.model, 'rb') as f:
        model = json.load(f)
        rdf.purge_terms(model)
        graph = rdf.graph_from_model(model)

    book = xl.load(args.book)

    for transform in args.transform:
        tf = trans.Transform.from_name(transform)
        sheet = xl.sheet(book, tf.sheet)
        triples = tf.process(graph, xl.as_rows(sheet, tf.required_rows()))

        if args.verbose:
            triples = list(triples)
            subgraph = rdf.graph_from_triples(triples)
            print(subgraph.serialize(format='turtle').decode('utf-8'))

        rdf.update_model_terms(model, triples)

    with open(args.model_out, 'w') as f:
        json.dump(model, f)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
