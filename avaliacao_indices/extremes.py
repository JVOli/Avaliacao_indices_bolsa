"""Utilitários para análise de dias extremos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd


@dataclass(slots=True)
class ExtremeContribution:
    """Resumo do impacto de dias extremos."""

    base_cagr: float
    adjusted_cagr: float
    base_sharpe: float
    adjusted_sharpe: float
    base_volatility: float
    adjusted_volatility: float


def remove_extreme_days(
    returns: pd.Series,
    *,
    top_n_positive: Optional[int] = None,
    top_n_negative: Optional[int] = None,
) -> pd.Series:
    """Remove dias extremos positivos/negativos da série de retornos."""

    cleaned = returns.dropna()
    if cleaned.empty:
        return cleaned

    to_drop: Dict[pd.Timestamp, float] = {}

    if top_n_positive:
        largest = cleaned.nlargest(top_n_positive)
        to_drop.update({idx: val for idx, val in largest.items()})

    if top_n_negative:
        smallest = cleaned.nsmallest(top_n_negative)
        to_drop.update({idx: val for idx, val in smallest.items()})

    return cleaned.drop(index=to_drop.keys(), errors="ignore")


def compute_extreme_contribution(
    returns: pd.Series,
    *,
    analyzer,
    top_n_positive: int = 5,
    top_n_negative: int = 5,
    ) -> ExtremeContribution:
    """Calcula o impacto dos dias extremos em métricas de desempenho."""

    returns = returns.dropna()
    if returns.empty:
        raise ValueError("Retornos insuficientes para análise de extremos")

    prices = (1 + returns).cumprod()
    metrics_base = analyzer.compute_from_returns(returns)

    adjusted_returns = remove_extreme_days(
        returns,
        top_n_positive=top_n_positive,
        top_n_negative=top_n_negative,
    )
    metrics_adjusted = analyzer.compute_from_returns(adjusted_returns)

    return ExtremeContribution(
        base_cagr=metrics_base.cagr,
        adjusted_cagr=metrics_adjusted.cagr,
        base_sharpe=metrics_base.sharpe,
        adjusted_sharpe=metrics_adjusted.sharpe,
        base_volatility=metrics_base.annualized_vol,
        adjusted_volatility=metrics_adjusted.annualized_vol,
    )

