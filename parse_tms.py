import sys

import tm


WS = "\t "
TMS_BLANK_SYM = "_"
DIR_TRANSLATION = {"<": tm.Dir.LEFT, "-": tm.Dir.HOLD, ">": tm.Dir.RIGHT}


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


class ParseException(Exception):
    pass


def parse(contents):
    i = 0

    orig_lines = contents.split("\n")
    no_ws = (line.strip(WS) for line in orig_lines)
    no_empties = (line for line in no_ws if line)
    no_commlines = (line for line in no_empties if not line.startswith("//"))

    lines = []
    for line in no_commlines:
        good_line = line
        idx = good_line.find("//")
        if idx != -1:
            good_line = good_line[:idx]

        good_line = good_line.rstrip(WS)
        lines.append(good_line)

    i = 0
    n = len(lines)
    init_state = None
    delta = {}
    while i < n:
        original_line = lines[i]
        line = original_line.strip(WS)
        idx = line.find("//")
        if idx != -1:
            line = line[:idx]

        if not line or line.startswith("name:") or line.startswith("accept:"):
            i += 1
            continue

        if line.startswith("init:"):
            init_state = line[len("init:"):].strip(WS)
            i += 1
            continue

        for ws in WS:
            line = line.replace(ws, "")

        try:
            state, sym = line.split(",")
            if sym == TMS_BLANK_SYM:
                sym = tm.BLANK_SYM


            i += 1
            found = False
            while not found:
                original_line = lines[i]
                line = original_line.strip(WS)
                idx = line.find("//")
                if idx != -1:
                    line = line[:idx]

                if not line or line.startswith("name:") or line.startswith("accept:"):
                    i += 1
                    continue

                if line.startswith("init:"):
                    init_state = line[len("init:"):].strip(WS)
                    i += 1
                    continue

                for ws in WS:
                    line = line.replace(ws, "")

                found = True

            nstate, nsym, ndir = line.split(",")
            if nsym == TMS_BLANK_SYM:
                nsym = tm.BLANK_SYM

            delta[(state, sym)] = (nstate, nsym, DIR_TRANSLATION[ndir])
        except ValueError as e:
            print(e)
            raise ParseException(f"Malformed transition in line {i}: \"{original_line}\"")

        i += 1

    if init_state is None:
        raise ParseException("Initial state not defined!")

    return tm.TuringMachine(init_state, delta)


def parse_tms(path):
    with open(path) as fin:
        contents = fin.read()

    try:
        machine = parse(contents)
    except ParseException as e:
        eprint(e)
        sys.exit(1)

    return machine
