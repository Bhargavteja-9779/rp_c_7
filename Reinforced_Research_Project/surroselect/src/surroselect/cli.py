"""Command-line interface.  Three commands, all working on plain files (.npz with arrays X (runs x inputs) and Y (runs x outputs)):
  surroselect fit      data.npz --model model.pkl [--target 0.01] [--cv 4] [--report report.md] [--no-curve]
  surroselect predict  model.pkl X_new.npz|.npy --out Y_pred.npy
  surroselect evaluate model.pkl test.npz            # prints the mean relative L2 error of the saved model on held-out X, Y
(`surroselect data.npz ...` without a command is kept as a shortcut for `fit`.)"""
from __future__ import annotations
import argparse, json, pickle, sys, numpy as np
from .select import SurrogateSelector
from .report import make_report


def _load_xy(path):
    z = np.load(path); return z["X"], z["Y"]


def cmd_fit(a):
    X, Y = _load_xy(a.data); sel = SurrogateSelector(cv=a.cv, random_state=a.seed, verbose=a.verbose).fit(X, Y)
    if not a.no_curve: sel.learning_curve()
    rep = make_report(sel, a.target); print(rep)
    if a.model:
        sel._X = sel._Y = None; sel.pool_ = None; sel.all_models_ = None; sel.folds_ = None            # keep only what prediction needs
        pickle.dump(sel, open(a.model, "wb"))
    if a.report: open(a.report, "w").write(rep)
    if a.json: json.dump(dict(selected=sel.best_name_, cv_error=sel.best_cv_error_, ties=sel.ties_, cv_table=[{k: r[k] for k in ("name", "cv_error", "seconds")} for r in sel.cv_table_], floor=sel.floor_report_, curve=getattr(sel, "curve_", None)), open(a.json, "w"), indent=1, default=float)
    return 0


def cmd_predict(a):
    sel = pickle.load(open(a.model, "rb")); p = a.x
    X = np.load(p)["X"] if p.endswith(".npz") else np.load(p); Yh = sel.predict(X)
    np.save(a.out, Yh); print(f"wrote {a.out} with shape {Yh.shape}"); return 0


def cmd_evaluate(a):
    sel = pickle.load(open(a.model, "rb")); X, Y = _load_xy(a.data); Yh = sel.predict(X)
    err = float(np.mean(np.linalg.norm(Y - Yh, axis=1) / (np.linalg.norm(Y, axis=1) + 1e-300))); print(f"mean relative L2 error of {sel.best_name_} on {len(X)} held-out runs: {err:.4e}")
    if a.json: json.dump(dict(model=sel.best_name_, n=len(X), mean_relative_l2_error=err), open(a.json, "w"))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in ("fit", "predict", "evaluate", "-h", "--help"): argv = ["fit"] + argv            # shortcut
    ap = argparse.ArgumentParser(prog="surroselect", description="Choose a stand-in model for a slow simulation."); sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit", help="select a model by cross-validation, report ties, basis check, learning curve"); f.add_argument("data"); f.add_argument("--model", default=None); f.add_argument("--target", type=float, default=None)
    f.add_argument("--cv", type=int, default=4); f.add_argument("--seed", type=int, default=0); f.add_argument("--report", default=None); f.add_argument("--json", default=None); f.add_argument("--no-curve", action="store_true"); f.add_argument("--verbose", action="store_true"); f.set_defaults(fn=cmd_fit)
    p = sub.add_parser("predict", help="apply a saved model to new inputs"); p.add_argument("model"); p.add_argument("x"); p.add_argument("--out", required=True); p.set_defaults(fn=cmd_predict)
    e = sub.add_parser("evaluate", help="error of a saved model on held-out data"); e.add_argument("model"); e.add_argument("data"); e.add_argument("--json", default=None); e.set_defaults(fn=cmd_evaluate)
    a = ap.parse_args(argv); return a.fn(a)


if __name__ == "__main__": sys.exit(main())
