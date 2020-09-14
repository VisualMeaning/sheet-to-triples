# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Convert tabular data into triples."""

import argparse
import sys

from . import (
    debug,
    run,
    trans,
)


def parse_args(argv):
    parser = argparse.ArgumentParser(argv[0], description=__doc__)
    parser.add_argument(
        '--book', action='append',
        help='paths to any spreadsheet files to load')
    parser.add_argument(
        '--model', help='path to json file with existing map model')
    parser.add_argument(
        '--model-out', metavar='PATH', default='new.json',
        help='path to write new jsom file with output map model')
    parser.add_argument(
        '--debug', action='store_true', help='debug interactively any error')
    parser.add_argument(
        '--verbose', action='store_true', help='show details as turtle')
    parser.add_argument(
        'transform', nargs='*', type=trans.Transform.from_name,
        help='names of any transforms to run')
    args = parser.parse_args(argv[1:])

    if not args.book:
        need_book = set(tf.name for tf in args.transform if tf.uses_sheet())
        if need_book:
            parser.error(f'transforms {need_book} require --book')
    return args


def main(argv):
    args = parse_args(argv)
    runner = run.Runner.from_args(args)

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
