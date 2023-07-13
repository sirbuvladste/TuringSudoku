import tm


WS = "\t "
TMS_BLANK_SYM = "_"
DEFAULT_NAME = "machine"
DIR_TRANSLATION = {tm.Dir.LEFT: "<", tm.Dir.HOLD: "-", tm.Dir.RIGHT: ">"}



def serialize_tms(machine, name=DEFAULT_NAME):
    result = ""
    result += f"name: {name}\n"
    result += f"init: {machine.init_state}\n"
    result += "accept: H, Y\n\n"

    for ((state, sym), (nstate, nsym, direction)) in machine.delta.items():
        dir_str = DIR_TRANSLATION[direction]
        if tm.is_blank(sym):
            sym = "_"

        if tm.is_blank(nsym):
            nsym = "_"

        result += f"{state},{sym}\n"
        result += f"{nstate},{nsym},{dir_str}\n\n"

    return result

def write_tms(path, machine):
    output = serialize_tms(machine)

    with open(path, "w") as fout:
        fout.write(output)
