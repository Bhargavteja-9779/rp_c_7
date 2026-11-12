"""Cost-benefit arithmetic for replacing a slow solver by a stand-in model."""
from __future__ import annotations


def cost_benefit(solver_seconds, n_train, tool_seconds=0.0, n_queries=None, predict_seconds=0.0):
    """Compare running the solver for every query with training a stand-in on `n_train` runs.

    solver_seconds: time of one solver run; n_train: runs spent on training data; tool_seconds: time of SurroSelect (cross-validated fit etc.);
    n_queries: number of future evaluations the user expects (optional); predict_seconds: time of one stand-in evaluation.
    Returns a dict: surrogate_fixed_seconds, break_even_queries (queries after which the stand-in is cheaper; None if never) and, if n_queries is given, both totals.
    The comparison ignores validation runs, parallel solver evaluation and the accuracy lost; it is an upper bound on the saving."""
    if solver_seconds <= 0: raise ValueError("solver_seconds must be positive")
    fixed = n_train * solver_seconds + tool_seconds; saving = solver_seconds - predict_seconds
    out = dict(surrogate_fixed_seconds=float(fixed), break_even_queries=(float(fixed / saving) if saving > 0 else None))
    if n_queries is not None: out.update(direct_seconds=float(n_queries * solver_seconds), surrogate_total_seconds=float(fixed + n_queries * predict_seconds), n_queries=n_queries)
    return out
