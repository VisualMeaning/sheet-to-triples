# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Convert tabular data into triples."""

import argparse
import itertools
import os
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


def _is_book_path(path):
    return path.endswith(('.xls', '.xlsx'))


def _parse_book_path(path):
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for filepath in filter(_is_book_path, files):
                yield os.path.join(root, filepath)
            return
    else:
        yield path


def _parse_transform_list(path):
    transforms = []
    with open(path, 'r') as f:
        for transform in f.read().splitlines():
            transforms.extend(trans.Transform.iter_from_name(transform))
    return transforms


def parse_args(argv):
    parser = argparse.ArgumentParser(argv[0], description=__doc__)
    parser.add_argument(
        '--book', action='extend', type=_parse_book_path,
        help='paths to any spreadsheet files to load')
    parser.add_argument(
        '--add-graph', action='append',
        help='path to existing graph to add to model')
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
        '--from-list', type=_parse_transform_list,
        help='add multiple transforms from a text file of transform names')
    parser.add_argument(
        '--non-unique-from', type=_parse_transform_list,
        help='load non unique triple properties from list of past transforms')
    parser.add_argument(
        'transform', nargs='*', type=trans.Transform.iter_from_name,
        help='names of any transforms to run')
    args = parser.parse_args(argv[1:])
    # need to flatten this slightly awkward way as action=extend doesn't work
    args.transform = list(itertools.chain(*args.transform))
    if args.from_list:
        args.transform.extend(args.from_list)
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
        for graph_to_add in args.add_graph:
            runner.graph.parse(graph_to_add, format='ttl')
        runner.model['terms'] = []
        rdf.update_model_terms(runner.model, iter(runner.graph))

    with debug.context(args.debug):
        if args.non_unique_from:
            runner.use_non_uniques(args.non_unique_from)
        if args.transform:
            runner.run(args.transform)
            if runner.model:
                runner.save_model(args.model_out)
        elif runner.verbose:
            run.show_graph(runner.graph)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
