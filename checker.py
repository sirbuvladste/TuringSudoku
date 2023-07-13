#!/usr/bin/env python3
import argparse
from enum import IntEnum
import os
import sys

from parse_tms import parse_tms
from parse_xlsx import parse_xlsx
from write_tms import write_tms
from write_xlsx import write_xlsx
import tm


from tests import TESTS


LOGDIR = "logs/"
MAX_STEPS = 100000

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


class What(IntEnum):
    LINE = 0
    COL = 1
    REGION = 2
    ALL = 3


CRITTERIA_DICT = {
        "lines": What.LINE,
        "columns": What.COL,
        "regions": What.REGION,
        "all": What.ALL,
    }


def what_to_str(what):
    if what == What.LINE:
        return "lines"
    elif what == What.COL:
        return "columns"
    elif what == What.REGION:
        return "square"
    else:
        return "all"


def run_on_input(machine, args):
    res = machine.run(word=args.test_input, max_steps=args.max_steps,
                      debug=True)


def run_test(machine, args, test, what, log):
    word, critteria = test

    res = machine.run(word=word, max_steps=args.max_steps, debug=True,
                      dbglog=log)

    if what == What.ALL:
        ref = critteria[0] and critteria[1] and critteria[2]
    else:
        ref = critteria[what]

    return res == ref


def run_test_suit(machine, what, args, tests=TESTS, logdir=LOGDIR):
    total = 0
    os.makedirs(logdir, exist_ok=True)

    print(f"Testing {what_to_str(what)} verification:")
    for i, test in enumerate(tests.items()):
        dbglog = os.path.join(LOGDIR, f"dbglog_{i+1}")

        print(f"#{i+1:<3} ({test[0]})", "."*40, sep=" ", end=" ")
        try:
            res = run_test(machine, args, test, what, dbglog)
            print("PASS" if res else "FAIL")
            total += res
        except tm.StepLimitExceeded:
            print("SLE")

    print()
    return total


def run_tests(machine, args, tests=TESTS):
    if not isinstance(args.validation_type, list):
        critteria = [CRITTERIA_DICT[args.validation_type]]
    else:
        critteria = [CRITTERIA_DICT[c] for c in args.validation_type]

    max_score = len(tests)
    total = 10

    if "all" in args.validation_type:
        total_max_score = 100
    else:
        total_max_score = 10 + 30 * len(critteria)

    for what in critteria:
        cscore = run_test_suit(machine, what, args, tests)
        if what == What.ALL:
            cscore *= 3

        total += cscore
        if len(critteria) > 1:
            print(f"Critteria score: {cscore}/{max_score}\n")

    print(f"Total: {total}/{total_max_score}")


def parse_machine(path):
    extension = path.split(".")[-1]
    if extension == "tms":
        return parse_tms(path)
    elif extension == "xlsx":
        return parse_xlsx(path)
    else:
        raise ValueError(f"Don't know what to do with {path} (valid \
                extensions are \".tms\" and \".xlsx\"")


def write_machine(machine, args):
    path = args.output
    extension = path.split(".")[-1]
    if extension == "tms":
        return write_tms(path, machine)
    elif extension == "xlsx":
        return write_xlsx(path, machine)
    else:
        raise ValueError(f"Don't know what to do with {path} (valid \
                extensions are \".tms\" and \".xlsx\"")


def main():
    parser = argparse.ArgumentParser(description="Checker for the first \
            assignment for the Analysis of Algorithm course. \
            The main functionality is to load a Turing Machine and either \
            run it on some input or convert it to another format.")
    parser.add_argument("--tm", help="Input Turing Machine file (.xlsx or \
                        .tms)", required=True)
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS,
            help="Maximum number of steps a TM is allowed to make before a \
            \"Step Limit Exceded\" error is produced. Default is %(default)s.")
    tgroup = parser.add_mutually_exclusive_group(required=True)
    tgroup.add_argument("--run-tests", action="store_true", help="Run the \
                        machine on all tests")
    tgroup.add_argument("--test-input", type=str, help="Test a specific input")
    tgroup.add_argument("--output", help="Output Turing Machine file (.xlsx \
            or .tms).")
    parser.add_argument("--validation-type", choices=["lines", "columns",
    "regions", "all"], nargs="+", default="all", help="Choose which kind of \
            checks are performed (by default, they all are).")

    args = parser.parse_args()

    path = args.tm
    machine = parse_machine(path)

    if os.path.exists("README") and not args.validation_type:
        with open("README", "r") as fin:
            first = fin.readline().strip("\n")

        critteria = first.split(" ")
        validation_type = []
        valid_line = True
        for crit in critteria:
            if crit not in ["lines", "columns", "regions"]:
                valid_line = False

            validation_type.append(crit)

        if valid_line:
            args.validation_type = validation_type

    if args.run_tests:
        run_tests(machine, args)
    elif args.test_input:
        try:
            run_on_input(machine, args)
        except tm.StepLimitExceeded:
            eprint("Step Limit Exceeded!")
    elif args.output:
        write_machine(machine, args)


if __name__ == "__main__":
    main()
