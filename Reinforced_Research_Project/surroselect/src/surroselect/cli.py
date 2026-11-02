from __future__ import annotations
import argparse, numpy as np
from .select import SurrogateSelector
from .report import make_report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="surroselect", description="Choose a stand-in model for a slow simulation. Input: .npz with X (runs x inputs) and Y (runs x outputs).")
    ap.add_argument("data", help=".npz with arrays X and Y"); ap.add_argument("--target", type=float, default=None, help="target mean relative error, e.g. 0.01")
    ap.add_argument("--cv", type=int, default=4); ap.add_argument("--out", default=None, help="write the report to this file"); ap.add_argument("--no-curve", action="store_true")
    a = ap.parse_args(argv); z = np.load(a.data); sel = SurrogateSelector(cv=a.cv, verbose=True).fit(z["X"], z["Y"])
    if not a.no_curve: sel.learning_curve()
    rep = make_report(sel, a.target); print(rep)
    if a.out: open(a.out, "w").write(rep)


if __name__ == "__main__": main()
