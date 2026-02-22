indent = "    "
vert = "│"
horz = "─"
tee = "├──"
corner = "└──"
arrow = "→"
delta = "∆"

SPACER_COL = 60


def build_spacer(x: str):
    pos = x.find("__SPACER__")
    reps = max(1, SPACER_COL - pos)
    return " " + horz * reps + vert + " "
