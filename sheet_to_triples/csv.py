# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Extract data from a graph as csv."""

import argparse
import csv
import sys

from rdflib.plugins import sparql

from . import (
    debug,
    rdf,
    run,
)


# Hardcode mapping here for now
QUERIES = {
    'painpoints': """
SELECT ?Stakeholder ?Name ?Type ?Description ?Coordinates WHERE {
    ?Id rdf:type vm:Painpoint ;
        vm:name ?Name ;
        vm:description ?Description ;
        vm:ofStakeholder ?SId ;
        vm:harmsCapitalType ?TId ;
        vm:atGeoPoint ?Coordinates ;
    .
    ?SId vm:name ?Stakeholder .
    BIND(SUBSTR(STR(?TId), 44) as ?Type) .
} ORDER BY ?Stakeholder ?Name
""",
}


def _named_query(value):
    try:
        return QUERIES[value]
    except KeyError:
        raise ValueError


def write_csv(filename, fieldnames, iter_rows):
    with open(filename, 'w', newline='\r\n') as f:
        writer = csv.DictWriter(f, lineterminator='\n', fieldnames=fieldnames)
        writer.writeheader()
        for row in iter_rows:
            writer.writerow(row)


def parse_args(argv):
    parser = argparse.ArgumentParser(argv[0], description=__doc__)
    parser.add_argument(
        '--csv', default='out.csv', help='path to write new csv file')
    parser.add_argument(
        '--model', required=True,
        help='path to json file with existing map model')
    parser.add_argument(
        '--debug', action='store_true', help='debug interactively any error')
    parser.add_argument(
        '--verbose', action='store_true', help='show details as turtle')
    parser.add_argument(
        'query', type=_named_query, help='sparql query to generate csv')
    return parser.parse_args(argv[1:])


def main(argv):
    args = parse_args(argv)
    graph = rdf.graph_from_model(run.Runner.load_model(args.model))

    with debug.context(args.debug):
        q = sparql.prepareQuery(args.query, initNs=dict(graph.namespaces()))
        result = graph.query(q)
        if result:
            rows = list(map(str, q.algebra['PV']))
            write_csv(args.csv, rows, (r.asdict() for r in result))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
