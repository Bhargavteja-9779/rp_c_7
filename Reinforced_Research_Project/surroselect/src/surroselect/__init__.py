"""SurroSelect: choose a fast stand-in (surrogate) for a slow simulation."""
from .select import SurrogateSelector, TIE_BAND_DECADES
from .models import PodGP, GPFull, PodKRRWide, PodPoly, POD, rel_l2, default_candidates, make_candidate, nrmse, get_metric
from .report import make_report
__version__ = "0.1.0"
