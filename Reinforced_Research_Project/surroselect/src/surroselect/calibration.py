"""Empirical interval for the budget forecast.

Provenance: 960 forecasts (54 benchmark problems x 3 seeds x 3 starting budgets N0 in {64, 128, 256} x horizons 2 and 4) of the test error of the selected model, made from the cross-validated learning curve
with the power-law forecast of `SurrogateSelector.predict_error`. Q_* are the 80 % and 90 % quantiles of |log10(actual) - log10(forecast)| over the 792 development cases.
Checks (post hoc, see the paper): leave-one-family-out coverage of the 80 % / 90 % intervals on the development cases 79 % / 89 %; on 168 held-out cases (10 problems, 4 families not used in the calibration) 85 % / 98 %.
The intervals are wide (about 1.2 and 2.4 decades) and the error grows with N0; they are an honest statement of how rough the forecast is, not a precise uncertainty model."""
Q80, Q90 = 0.5794, 1.1756                 # decades (log10 units)
TYPICAL_FACTOR = dict(median=1.48, p80=3.63, p90=11.1)       # factor between actual and forecast error: 50 %, 80 %, 90 % of the 960 forecasts
VERSION = "1"


def interval_decades(level=0.8):
    if abs(level - 0.8) < 1e-9: return Q80
    if abs(level - 0.9) < 1e-9: return Q90
    raise ValueError("level must be 0.8 or 0.9 (the only levels that were calibrated)")
