from __future__ import annotations


def make_report(sel, target=None, unit="mean relative L2 error"):
    """Plain-text/markdown report of a fitted SurrogateSelector."""
    L = [f"# SurroSelect report", f"{sel.n_train_} runs, {sel.p_} inputs, {sel.m_} outputs. Cross-validated {unit} ({sel.cv} folds).", "", "| model | CV error | within tie band of best | seconds |", "|---|---:|:---:|---:|"]
    for r in sel.cv_table_: L.append(f"| {r['name']} | {r['cv_error']:.3e} | {'yes' if r['name'] in sel.ties_ else ''} | {r['seconds']:.1f} |")
    L += ["", f"**Selected:** {sel.best_name_} (CV error {sel.best_cv_error_:.2e}). Models tied with it (within {10**sel.tie_band:.2f}x): {', '.join(sel.ties_)}.", ""]
    f = sel.floor_report_; L += [f"**Basis check.** Best POD-based model: {f['best_pod_model']} (CV error {f['best_pod_cv_error']:.2e}); error of projecting held-out fields on a {f['rank']}-mode basis: {f['pod_floor_cv']:.2e}. {f['advice']}"]
    if getattr(sel, "curve_", None) is not None:
        cv = sel.curve_; L += ["", "**Learning curve** (" + cv["name"] + "): " + ", ".join(f"n={n:.0f}: {e:.2e}" for n, e in zip(cv["n"], cv["error"]))]
        c, lo, hi = sel.predict_error(4 * sel.n_train_); L.append(f"Extrapolated error with {4*sel.n_train_} runs: about {c:.1e} (range {min(lo,hi):.1e} to {max(lo,hi):.1e}); extrapolation over 4x the data is a rough guide only.")
        if target is not None:
            n = sel.runs_needed(target); L.append(f"Runs needed for error {target:g}: " + (f"about {n:.0f}" if n else "cannot be estimated reliably (flat curve or more than 16x the current budget)") + ".")
    return "\n".join(L)
