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
    parser.add_argument('trans')
    parser.add_argument('book')
    parser.add_argument('model')
    args = parser.parse_args(argv[1:])

    tf = trans.Transform.from_name(args.trans)
    sheet = xl.load(args.book, tf.sheet)
    rows = list(xl.as_rows(sheet, tf.required_rows()))
    with open(args.model, 'rb') as f:
        graph = rdf.graph_from_model(json.load(f))
    new = rdf.rdflib.Graph(base=rdf.VM)
    for t in tf.process(graph, rows):
        new.add(t)
    print(new.serialize(format="turtle").decode("utf-8"))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
