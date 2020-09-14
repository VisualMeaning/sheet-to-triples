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


def main(argv):
    parser = argparse.ArgumentParser(argv[0], description=__doc__)
    parser.add_argument('--book', action='append')
    parser.add_argument('--model')
    parser.add_argument('--model-out', metavar='PATH', default='new.json')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('transform', nargs='*', type=trans.Transform.from_name)
    args = parser.parse_args(argv[1:])

    if not args.book:
        need_book = set(tf.name for tf in args.transform if tf.uses_sheet())
        if need_book:
            parser.error(f'transforms {need_book} require --book')

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
