from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm


def infer_periods_per_year(index: pd.DatetimeIndex) -> int:
    if len(index) < 2:
        return 252
    freq = pd.infer_freq(index)
    if freq is None:
        # fallback por densidade média de amostras/dia
        days = (index[-1] - index[0]).days or 1
        approx = len(index) / days
        if approx > 0.6:
            return 252
        if approx > 0.12:
            return 52
        return 12
    freq = freq.upper()
    if freq.startswith("B") or freq == "D":
        return 252
    if freq.startswith("W"):
        return 52
    if freq.startswith("M"):
        return 12
    if freq.startswith("Q"):
        return 4
    if freq.startswith("A") or freq.startswith("Y"):
        return 1
    return 252


def to_returns_from_prices(prices: pd.Series | pd.DataFrame, method: str = "pct_change") -> pd.Series | pd.DataFrame:
    if method == "log":
        return np.log(prices / prices.shift(1)).dropna()
    return prices.pct_change().dropna()


def align_excess_returns(r: pd.Series | pd.DataFrame, r_free: pd.Series) -> pd.Series | pd.DataFrame:
    r_free = r_free.reindex(r.index).fillna(0.0)
    if isinstance(r, pd.Series):
        return r - r_free
    r_f = pd.concat([r_free] * r.shape[1], axis=1)
    r_f.index = r.index
    r_f.columns = r.columns
    return r - r_f


def annualize_return(r: pd.Series, periods_per_year: Optional[int] = None) -> float:
    if periods_per_year is None:
        periods_per_year = infer_periods_per_year(r.index)
    compounded_growth = (1 + r).prod()
    n_periods = r.shape[0]
    return compounded_growth ** (periods_per_year / n_periods) - 1


def annualize_volatility(r: pd.Series, periods_per_year: Optional[int] = None) -> float:
    if periods_per_year is None:
        periods_per_year = infer_periods_per_year(r.index)
    return float(r.std(ddof=0) * np.sqrt(periods_per_year))


def semideviation(r: pd.Series) -> float:
    negative = r[r < 0]
    return float(negative.std(ddof=0))


def sharpe_ratio(r: pd.Series) -> float:
    ppyear = infer_periods_per_year(r.index)
    mu = r.mean() * ppyear
    vol = r.std(ddof=0) * np.sqrt(ppyear)
    return float(np.nan if vol == 0 else mu / vol)


def sortino_ratio(r: pd.Series) -> float:
    ppyear = infer_periods_per_year(r.index)
    mu = r.mean() * ppyear
    sd = semideviation(r) * np.sqrt(ppyear)
    return float(np.nan if sd == 0 else mu / sd)


def drawdown_series(r: pd.Series) -> pd.DataFrame:
    wealth = (1 + r).cumprod()
    peaks = wealth.cummax()
    dd = wealth / peaks - 1.0
    return pd.DataFrame({"wealth": wealth, "peak": peaks, "drawdown": dd})


def calmar_ratio(r: pd.Series) -> float:
    ann_ret = annualize_return(r)
    dd = drawdown_series(r)["drawdown"].min()
    return float(np.nan if dd == 0 else ann_ret / abs(dd))


def regression_alpha_beta(y: pd.Series, x: pd.Series) -> Tuple[float, float, float]:
    df = pd.concat([y, x], axis=1).dropna()
    if df.empty:
        return np.nan, np.nan, np.nan
    X = sm.add_constant(df.iloc[:, 1].values)
    model = sm.OLS(df.iloc[:, 0].values, X).fit()
    alpha = float(model.params[0])
    beta = float(model.params[1])
    r2 = float(model.rsquared)
    return alpha, beta, r2


def herfindahl_hirschman_index(weights: pd.Series | pd.DataFrame) -> float:
    if isinstance(weights, pd.DataFrame):
        w = weights.iloc[-1].dropna()
    else:
        w = weights.dropna()
    w = w / w.sum()
    return float((w ** 2).sum())


def diversification_ratio(weights: pd.Series, cov: pd.DataFrame) -> float:
    w = weights / weights.sum()
    asset_vols = np.sqrt(np.diag(cov.values))
    portfolio_vol = np.sqrt(float(w.values @ cov.values @ w.values))
    if portfolio_vol == 0:
        return np.nan
    return float((w.values @ asset_vols) / portfolio_vol)


@dataclass
class Summary:
    annual_return: float
    annual_vol: float
    sharpe: float
    sortino: float
    calmar: float
    max_drawdown: float


def summarize_series(r: pd.Series) -> Summary:
    dd = drawdown_series(r)["drawdown"].min()
    return Summary(
        annual_return=annualize_return(r),
        annual_vol=annualize_volatility(r),
        sharpe=sharpe_ratio(r),
        sortino=sortino_ratio(r),
        calmar=calmar_ratio(r),
        max_drawdown=float(dd),
    )


