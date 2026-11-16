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
        if any(b > a for a, b in zip(cv["error"], cv["error"][1:])): L.append("**Note: the learning curve is not monotone** (the error rises with more runs at some point), so the power-law forecast below is unreliable; treat it as a guess.")
        lo, c, hi = sel.forecast_interval(4 * sel.n_train_); L.append(f"Extrapolated error with {4*sel.n_train_} runs: about {c:.1e}; empirical 80% interval {lo:.1e} to {hi:.1e} (about a factor 3.8 each way). In 960 forecasts on 54 test problems the actual error was within a factor 1.5 of the forecast in half of the cases, within 3.6 in 80% and within 11 in 90%; forecasts were wrong by more than a factor two in about a third of the cases. Treat the forecast as a rough guide.")
        if target is not None:
            n = sel.runs_needed(target); nc = sel.runs_needed_confident(target); L.append(f"Runs needed for error {target:g}: " + (f"about {n:.0f}" if n else "cannot be estimated reliably (flat curve or more than 16x the current budget)") + (f"; to be 80% sure (upper end of the interval below the target): about {nc:.0f}" if nc else ("; no confident estimate within 16x the current budget" if n else "")) + ".")
    if solver_seconds is not None:
        from .cost import cost_benefit
        c = cost_benefit(solver_seconds, sel.n_train_, tool_seconds or 0.0, n_queries); L += ["", f"**Cost.** {sel.n_train_} runs at {solver_seconds:g} s take {sel.n_train_*solver_seconds/3600:.2f} h; with the tool the fixed cost is {c['surrogate_fixed_seconds']/3600:.2f} h, and the stand-in is cheaper than the solver after about {c['break_even_queries']:.0f} evaluations."
            + (f" For {n_queries} expected evaluations: solver {c['direct_seconds']/3600:.2f} h against {c['surrogate_total_seconds']/3600:.2f} h with the stand-in." if n_queries else "") + " Validation runs, parallel solver evaluation and the accuracy given up are not counted."]
    return "\n".join(L)
