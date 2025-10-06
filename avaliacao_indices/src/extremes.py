from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd

from .metrics import annualize_return, sharpe_ratio


def remove_top_n_days(r: pd.Series, n: int, best: bool = True) -> pd.Series:
    if n <= 0 or r.empty:
        return r
    r_sorted = r.sort_values(ascending=not best)
    to_remove = r_sorted.iloc[:n].index
    return r.drop(index=to_remove)


def impact_of_extremes(r: pd.Series, ns: Iterable[int]) -> pd.DataFrame:
    rows: List[dict] = []
    base_cagr = annualize_return(r)
    base_sharpe = sharpe_ratio(r)
    for n in ns:
        rb = remove_top_n_days(r, n=n, best=True)
        rw = remove_top_n_days(r, n=n, best=False)
        rows.append({
            "n": n,
            "scenario": "remove_best",
            "cagr": annualize_return(rb),
            "sharpe": sharpe_ratio(rb),
        })
        rows.append({
            "n": n,
            "scenario": "remove_worst",
            "cagr": annualize_return(rw),
            "sharpe": sharpe_ratio(rw),
        })
    df = pd.DataFrame(rows)
    df["base_cagr"] = base_cagr
    df["base_sharpe"] = base_sharpe
    return df


def event_study_after_extreme(r: pd.Series, q: float = 0.99, horizons: Iterable[int] = (1, 5, 20)) -> pd.DataFrame:
    th_up = r.quantile(q)
    th_dn = r.quantile(1 - q)
    events = pd.DataFrame({"r": r})
    events["is_up"] = r >= th_up
    events["is_dn"] = r <= th_dn
    out_rows: List[dict] = []
    for label, mask in [("top", events["is_up"]), ("bottom", events["is_dn"])]:
        event_dates = events.index[mask]
        for h in horizons:
            # retorno acumulado pós-evento
            acc = []
            for d in event_dates:
                window = r.loc[d:].iloc[1 : h + 1]
                if len(window) == h:
                    acc.append((1 + window).prod() - 1)
            out_rows.append({"side": label, "h": h, "avg": float(np.mean(acc) if acc else np.nan), "n": len(acc)})
    return pd.DataFrame(out_rows)


