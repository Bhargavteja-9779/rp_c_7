from __future__ import annotations


def make_report(sel, target=None, unit="mean relative L2 error", solver_seconds=None, n_queries=None, tool_seconds=None):
    """Plain-text/markdown report of a fitted SurrogateSelector."""
    L = [f"# SurroSelect report", f"{sel.n_train_} runs, {sel.p_} inputs, {sel.m_} outputs. Cross-validated {unit} ({sel.cv} folds).", "", "| model | CV error | within tie band of best | seconds |", "|---|---:|:---:|---:|"]
    for r in sel.cv_table_: L.append(f"| {r['name']} | {r['cv_error']:.3e} | {'yes' if r['name'] in sel.ties_ else ''} | {r['seconds']:.1f} |")
    if hasattr(sel, "usable_") and not sel.usable_:
        L += ["", f"**WARNING: no usable model.** The best cross-validated error ({sel.best_cv_error_:.2e}) exceeds {sel.usable_threshold:g}: no pool member predicts held-out runs well, and the selection below only ranks models that all fail. Add runs, change the inputs or outputs (e.g. smoother output quantities), or use a different model class."]
    L += ["", f"**Selected:** {sel.best_name_} (CV error {sel.best_cv_error_:.2e}). Models tied with it (within {10**sel.tie_band:.2f}x): {', '.join(sel.ties_)}.", ""]
    f = sel.floor_report_; L += [f"**Basis check.** Best POD-based model: {f['best_pod_model']} (CV error {f['best_pod_cv_error']:.2e}); error of projecting held-out fields on a {f['rank']}-mode basis: {f['pod_floor_cv']:.2e}. {f['advice']}"]
    if getattr(sel, "curve_", None) is not None:
        cv = sel.curve_; L += ["", "**Learning curve** (" + cv["name"] + "): " + ", ".join(f"n={n:.0f}: {e:.2e}" for n, e in zip(cv["n"], cv["error"]))]
        c, lo, hi = sel.predict_error(4 * sel.n_train_); L.append(f"Extrapolated error with {4*sel.n_train_} runs: about {c:.1e} (range {min(lo,hi):.1e} to {max(lo,hi):.1e}); extrapolation over 4x the data is a rough guide only (in the authors' evaluation on 16 test problems, about two thirds of such forecasts were within a factor two of the actual error, and they were more often too optimistic than too pessimistic).")
        if target is not None:
            n = sel.runs_needed(target); L.append(f"Runs needed for error {target:g}: " + (f"about {n:.0f}" if n else "cannot be estimated reliably (flat curve or more than 16x the current budget)") + ".")
    if solver_seconds is not None:
        from .cost import cost_benefit
        c = cost_benefit(solver_seconds, sel.n_train_, tool_seconds or 0.0, n_queries); L += ["", f"**Cost.** {sel.n_train_} runs at {solver_seconds:g} s take {sel.n_train_*solver_seconds/3600:.2f} h; with the tool the fixed cost is {c['surrogate_fixed_seconds']/3600:.2f} h, and the stand-in is cheaper than the solver after about {c['break_even_queries']:.0f} evaluations."
            + (f" For {n_queries} expected evaluations: solver {c['direct_seconds']/3600:.2f} h against {c['surrogate_total_seconds']/3600:.2f} h with the stand-in." if n_queries else "") + " Validation runs, parallel solver evaluation and the accuracy given up are not counted."]
    return "\n".join(L)
