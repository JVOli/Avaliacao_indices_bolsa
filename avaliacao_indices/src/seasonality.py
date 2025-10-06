from __future__ import annotations

from typing import Dict, Literal, Tuple

import numpy as np
import pandas as pd
from scipy import stats


def winsorize_series(r: pd.Series, limits: Tuple[float, float] = (0.01, 0.01)) -> pd.Series:
    if r.empty:
        return r
    lower = r.quantile(limits[0])
    upper = r.quantile(1 - limits[1])
    return r.clip(lower=lower, upper=upper)


def seasonality_by_month(r: pd.Series, winsorize: bool = True) -> pd.DataFrame:
    x = winsorize_series(r) if winsorize else r
    df = x.to_frame("ret")
    df["month"] = df.index.month
    grouped = df.groupby("month")["ret"]
    out = grouped.agg(["mean", "count", "std"]).rename(columns={"mean": "avg"})
    # teste t contra zero
    tvals = []
    pvals = []
    for m, g in grouped:
        if len(g) < 2:
            tvals.append(np.nan)
            pvals.append(np.nan)
        else:
            t, p = stats.ttest_1samp(g, 0.0, nan_policy="omit")
            tvals.append(t)
            pvals.append(p)
    out["t"] = tvals
    out["p"] = pvals
    return out


def seasonality_by_weekday(r: pd.Series, winsorize: bool = True) -> pd.DataFrame:
    x = winsorize_series(r) if winsorize else r
    df = x.to_frame("ret")
    df["weekday"] = df.index.weekday  # 0=Mon
    grouped = df.groupby("weekday")["ret"]
    out = grouped.agg(["mean", "count", "std"]).rename(columns={"mean": "avg"})
    # ANOVA simples (H0: médias iguais)
    groups = [g.values for _, g in grouped]
    if len(groups) >= 2:
        f, p = stats.f_oneway(*groups)
    else:
        f, p = np.nan, np.nan
    out["anova_F"] = f
    out["anova_p"] = p
    return out


