from openpyxl import Workbook

import tm


DIR_TRANSLATION = {tm.Dir.LEFT: "L", tm.Dir.HOLD: "S", tm.Dir.RIGHT: "R"}


def write_xlsx(path, machine):
    wb = Workbook()

    ws = wb.active
    ws.title = "Sheet1"

    symbols = [""] + sorted(set(pair[1] for pair in machine.delta.keys()))
    ws.append(symbols)

    init_state = machine.init_state

    states_raw = set(pair[0] for pair in machine.delta.keys()) - {init_state}
    states = ["", init_state] + sorted(states_raw)
    for state in states[1:]:
        state_line = [state]
        for sym in symbols[1:]:
            default_action = ("N", tm.BLANK_SYM, tm.Dir.HOLD)
            nstate, nsym, d = machine.delta.get((state, sym), default_action)
            d = DIR_TRANSLATION[d]

            state_line += [f"{nstate}, {nsym}, {d}"]

        ws.append(state_line)

    wb.save(filename=path)
