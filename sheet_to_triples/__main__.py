# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Convert tabular data into triples."""

import argparse
import sys

from . import (
    debug,
    rdf,
    run,
    trans,
)

PURGE_MAP = {
    'none': lambda _: True,
    'geo': rdf.relates_geo_name,
    'issues': rdf.relates_issue,
}


def parse_args(argv):
    parser = argparse.ArgumentParser(argv[0], description=__doc__)
    parser.add_argument(
        '--book', action='append',
        help='paths to any spreadsheet files to load')
    parser.add_argument(
        '--add-graph', help='path to existing graph to add to model')
    parser.add_argument(
        '--model', help='path to json file with existing map model')
    parser.add_argument(
        '--model-out', metavar='PATH', default='new.json',
        help='path to write new jsom file with output map model')
    arg_purge = parser.add_argument(
        '--purge-except', metavar='|'.join(PURGE_MAP.keys()),
        type=PURGE_MAP.get, default='none',
        help='Use named rule to remove some triples from existing model')
    parser.add_argument(
        '--debug', action='store_true', help='debug interactively any error')
    parser.add_argument(
        '--verbose', action='store_true', help='show details as turtle')
    parser.add_argument(
        '--spec', action='extend', type=trans.Transform.from_spec,
        help='add multiple transforms from a single spec file')
    parser.add_argument(
        'transform', nargs='*', type=trans.Transform.from_name,
        help='names of any transforms to run')
    args = parser.parse_args(argv[1:])
    if args.spec:
        args.transform.extend(args.spec)
    if not args.book:
        need_book = set(tf.name for tf in args.transform if tf.uses_sheet())
        if need_book:
            parser.error(f'transforms {need_book} require --book')
    if not args.purge_except:
        parser.error('--purge-except must be one of ' + arg_purge.metavar)
    return args


def main(argv):
    args = parse_args(argv)
    runner = run.Runner.from_args(args)
    if args.add_graph:
        runner.graph.parse(args.add_graph, format='ttl')
        runner.model['terms'] = []
        rdf.update_model_terms(runner.model, iter(runner.graph))

    with debug.context(args.debug):
        if args.transform:
            runner.run(args.transform)
            if runner.model:
                runner.save_model(args.model_out)
        elif runner.verbose:
            run.show_graph(runner.graph)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
