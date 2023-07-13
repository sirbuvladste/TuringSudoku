#!/usr/bin/env python
from array import array
from enum import Enum
import sys


BLANK_SYM = '□'
Y = 'Y'
N = 'N'
H = 'H'
DBGLOG = "debug.log"
MAX_STEPS = 100000


class StepLimitExceeded(Exception):
    pass


class Dir(Enum):
    LEFT = 1
    HOLD = 2
    RIGHT = 3


def is_blank(sym):
    return sym == BLANK_SYM


def _safe_get_array(arr: array, idx: int, filler):
    if idx >= len(arr):
        arr += array('u', filler * (idx - len(arr) + 1))

    return arr[idx]


class Tape():
    """Tape unbounded in both directions"""
    def __init__(self):
        self.left = array('u')
        self.right = array('u')

    def init(self, word):
        self.left = array('u')
        self.right = array('u', word)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            if idx >= 0:
                return _safe_get_array(self.right, idx, BLANK_SYM)
            else:
                idx = -idx + 1
                return _safe_get_array(self.left, idx, BLANK_SYM)
        elif isinstance(idx, slice):
            if idx.step is not None:
                raise NotImplementedError("Don't use steps in slices!")

            start, stop = idx.start, idx.stop
            if start is None:
                start = -len(self.left)
            if stop is None:
                stop = len(self.right)

            lb = -max(0, -stop - 1)
            le = -max(0, -start - 1)
            rb = max(0, start)
            re = max(0, stop)
            return self.left[lb:le] + self.right[rb:re]
        else:
            raise KeyError(f"Unusuable index: {idx} (of type {type(idx)}!")

    def __setitem__(self, idx: int, newsym: str):
        assert len(newsym) == 1
        self[idx]  # ensure the tape is resized if needed
        if idx >= 0:
            self.right[idx] = newsym
        else:
            idx = -idx + 1
            self.left[idx] = newsym


class TuringMachine():
    dir_translation = {Dir.LEFT: -1, Dir.HOLD: 0, Dir.RIGHT: 1}

    def __init__(self, init_state, delta):
        self.tape = Tape()
        self.init_state = init_state
        self.delta = delta

    def init(self, word):
        self.tape.init(word)
        self.pos = 0
        self.cstate = self.init_state

    def read(self):
        return self.tape[self.pos]

    def write(self, sym):
        self.tape[self.pos] = sym

    def move(self, d):
        offset = self.dir_translation[d]
        self.pos += offset

    def step(self):
        csym = self.read()
        default_tr = (N, BLANK_SYM, Dir.HOLD)
        nstate, nsym, ndir = self.delta.get((self.cstate, csym), default_tr)
        self.cstate = nstate
        self.write(nsym)
        self.move(ndir)

    def done(self):
        return self.cstate in {Y, N, H}

    def get_result(self):
        assert self.done()
        final_config = self.current_config()

        if final_config[2] == H:
            return final_config[1].rstrip(BLANK_SYM)
        else:
            return final_config[2] == Y

    def run(self, word=None, max_steps=MAX_STEPS, debug=False, dbglog=DBGLOG):
        if word is not None:
            self.init(word)

        if debug:
            dbglog = open(dbglog, "w")

        steps = 0
        try:
            while not self.done() and steps <= max_steps:
                if debug:
                    print(self.current_config(), file=dbglog)

                self.step()
                steps += 1;
        finally:
            print(self.current_config(), file=dbglog)
            if debug:
                dbglog.close()

        if steps > max_steps:
            raise StepLimitExceeded(f"Transition limit ({max_steps}) exceeded!")

        return self.get_result()

    def current_config(self):
        left = self.tape[:self.pos].tounicode()
        right = self.tape[self.pos:].tounicode()
        return (left, right, self.cstate)


def main():
    delta = {
            ('q1', '0'): ('q1', '1', Dir.RIGHT),
            ('q1', '1'): ('q1', '1', Dir.RIGHT),
            ('q1', BLANK_SYM): ('t', BLANK_SYM, Dir.LEFT),

            ('t', '0'): ('t', '1', Dir.LEFT),
            ('t', '1'): ('t', '1', Dir.LEFT),
            ('t', BLANK_SYM): ('H', BLANK_SYM, Dir.RIGHT),
    }

    t = TuringMachine('q1', delta)

    t.init("01011")
    print(t.current_config())
    result = t.run()
    print(result)
    print(t.current_config())


if __name__ == "__main__":
    main()
