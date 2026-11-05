"""Optional strong neural-network candidate: an MLP whose architecture, activation, learning rate and weight decay are tuned with Optuna (TPE + successive-halving pruning),
trained full-batch in float64 with Adam (cosine schedule), then retrained on all runs for 4x the epochs and polished with L-BFGS. Output either the full field or POD coefficients.
Requires torch and optuna. Selection uses a validation split of the training runs only."""
from __future__ import annotations
import copy, time, numpy as np
from .models import POD, rel_l2, get_metric


def _make(p, out, depth, width, act):
    import torch.nn as nn
    A = dict(tanh=nn.Tanh, silu=nn.SiLU, gelu=nn.GELU)[act]; L = []; d = p
    for _ in range(depth): L += [nn.Linear(d, width), A()]; d = width
    L.append(nn.Linear(d, out)); return nn.Sequential(*L).double()


def _train(net, X, T, epochs, lr, wd, report=None, lbfgs_iters=0):
    import torch
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=wd); sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    for ep in range(epochs):
        opt.zero_grad(); loss = ((net(X) - T) ** 2).mean(); loss.backward(); opt.step(); sched.step()
        if report is not None and (ep + 1) % max(1, epochs // 4) == 0: report(ep + 1, float(loss))
    if lbfgs_iters:
        o2 = torch.optim.LBFGS(net.parameters(), lr=1.0, max_iter=lbfgs_iters, line_search_fn="strong_wolfe", tolerance_grad=1e-12, tolerance_change=1e-14)
        def closure():
            o2.zero_grad(); l = ((net(X) - T) ** 2).mean(); l.backward(); return l
        o2.step(closure)
    return net


class TunedMLP:
    """Tuned MLP stand-in. fit(X, Y) with X in [0,1]^p (SurrogateSelector scales inputs)."""
    def __init__(self, n_trials=16, search_epochs=1500, final_factor=4, lbfgs_iters=200, seed=0, val_frac=0.2, verbose=False, metric="rel_l2", depth_range=(2, 4), widths=(64, 128, 256)):
        self.metric, self.depth_range, self.widths = metric, tuple(depth_range), tuple(widths)       # defaults = the search space of Stage 6
        self.n_trials, self.search_epochs, self.final_factor, self.lbfgs_iters, self.seed, self.val_frac, self.verbose = n_trials, search_epochs, final_factor, lbfgs_iters, seed, val_frac, verbose
    name = "tuned_mlp"
    def _targets(self, Y, kind, r):
        if kind == "pod": self.pod_ = POD(Y, r); A = self.pod_.encode(Y); self.sd_ = A.std(0) + 1e-12; return A / self.sd_
        self.pod_ = None; self.mean_ = Y.mean(0); self.s_ = float((Y - self.mean_).std() + 1e-12); return (Y - self.mean_) / self.s_
    def _decode(self, T, pod, sd=None, mean=None, s=None):
        return pod.decode(T * sd) if pod is not None else T * s + mean
    def fit(self, X, Y):
        import torch, optuna
        optuna.logging.set_verbosity(optuna.logging.WARNING); torch.set_num_threads(1); torch.manual_seed(self.seed)
        X = np.asarray(X, float); N, p = X.shape; rs = np.random.default_rng(self.seed); perm = rs.permutation(N); nv = max(2, int(self.val_frac * N)); va, tr = perm[:nv], perm[nv:]
        Xt, Xv = torch.tensor(X[tr]), torch.tensor(X[va])
        def objective(trial):
            kind = trial.suggest_categorical("kind", ["full", "pod"]); r = trial.suggest_categorical("r", [8, 16, 32]) if kind == "pod" else 0
            depth = trial.suggest_int("depth", *self.depth_range); width = trial.suggest_categorical("width", list(self.widths)); act = trial.suggest_categorical("act", ["tanh", "silu", "gelu"])
            lr = trial.suggest_float("lr", 1e-4, 1e-2, log=True); wd = trial.suggest_float("wd", 1e-9, 1e-3, log=True)
            pod = POD(Y[tr], r) if kind == "pod" else None
            if kind == "pod": A = pod.encode(Y[tr]); sd = A.std(0) + 1e-12; Tt = A / sd; mean = s = None
            else: mean = Y[tr].mean(0); s = float((Y[tr] - mean).std() + 1e-12); Tt = (Y[tr] - mean) / s; sd = None
            net = _make(p, Tt.shape[1], depth, width, act); Tt = torch.tensor(Tt)
            def val_err():
                with torch.no_grad(): Th = net(Xv).numpy()
                return get_metric(self.metric)(Y[va], self._decode(Th, pod, sd, mean, s), Y[tr])
            cnt = [0]
            def report(ep, loss):
                cnt[0] += 1; v = val_err(); trial.report(v, cnt[0])
                if trial.should_prune(): raise optuna.TrialPruned()
            _train(net, Xt, Tt, self.search_epochs, lr, wd, report=report); return val_err()
        study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=self.seed), pruner=optuna.pruners.SuccessiveHalvingPruner())
        study.enqueue_trial(dict(kind="full", depth=3, width=128, act="tanh", lr=1e-3, wd=1e-8)); study.optimize(objective, n_trials=self.n_trials, catch=(RuntimeError, ValueError))
        self.best_params_ = bp = study.best_params; self.best_val_error_ = study.best_value; kind, r = bp["kind"], bp.get("r", 0)
        T = self._targets(Y, kind, r); net = _make(p, T.shape[1], bp["depth"], bp["width"], bp["act"]); self.net_ = _train(net, torch.tensor(X), torch.tensor(T), self.search_epochs * self.final_factor, bp["lr"], bp["wd"], lbfgs_iters=self.lbfgs_iters)
        return self
    def predict(self, X):
        import torch
        with torch.no_grad(): T = self.net_(torch.tensor(np.asarray(X, float))).numpy()
        return self.pod_.decode(T * self.sd_) if self.pod_ is not None else T * self.s_ + self.mean_
