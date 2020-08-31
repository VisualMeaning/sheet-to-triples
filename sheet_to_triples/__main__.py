# Copyright 2020 Visual Meaning Ltd

"""Convert tabular data into triples."""

import argparse
import sys

from . import (
    run,
)


def main(argv):
    parser = argparse.ArgumentParser(argv[0], description=__doc__)
    parser.add_argument('--book')
    parser.add_argument('--model')
    parser.add_argument('--model-out', metavar='PATH', default='new.json')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('transform', nargs='*')
    args = parser.parse_args(argv[1:])

    runner = run.Runner.from_args(args)
    if args.transform:
        runner.run(args.transform)
        if args.model:
            runner.save_model(args.model_out)
    elif args.verbose:
        run.show_graph(runner.graph)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
