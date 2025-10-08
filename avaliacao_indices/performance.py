"""Cálculo de métricas de desempenho risco-retorno."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd


@dataclass(slots=True)
class PerformanceMetrics:
    """Container para métricas agregadas de performance."""

    total_return: float
    cagr: float
    annualized_vol: float
    sharpe: float
    sortino: float
    max_drawdown: float
    calmar: float
    information_ratio: Optional[float] = None


class PerformanceAnalyzer:
    """Calcula métricas de desempenho para séries de retornos."""

    def __init__(self, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> None:
        self.risk_free_rate = risk_free_rate
        self.periods_per_year = periods_per_year

    def compute_metrics(
        self,
        prices: pd.Series,
        *,
        benchmark: Optional[pd.Series] = None,
    ) -> PerformanceMetrics:
        """Retorna métricas para uma série temporal de preços."""

        aligned = prices.dropna()
        if aligned.empty:
            raise ValueError("Série de preços vazia")

        returns = aligned.pct_change().dropna()
        if returns.empty:
            raise ValueError("Não foi possível calcular retornos: série muito curta")

        benchmark_returns = None
        if benchmark is not None:
            benchmark_clean = benchmark.dropna()
            benchmark_clean = benchmark_clean.loc[aligned.index]
            benchmark_returns = benchmark_clean.pct_change().dropna()

        return self.compute_from_returns(returns, benchmark_returns=benchmark_returns)

    def compute_from_returns(
        self,
        returns: pd.Series,
        *,
        benchmark_returns: Optional[pd.Series] = None,
    ) -> PerformanceMetrics:
        """Calcula métricas diretamente a partir de uma série de retornos."""

        returns = returns.dropna()
        if returns.empty:
            raise ValueError("Série de retornos vazia")

        excess_return = returns - self._risk_free_periodic

        total_return = (1 + returns).prod() - 1
        cagr = (1 + total_return) ** (self.periods_per_year / len(returns)) - 1

        annualized_vol = returns.std() * np.sqrt(self.periods_per_year)
        downside_excess = excess_return.where(excess_return < 0.0, 0.0)
        downside_vol = downside_excess.std() * np.sqrt(self.periods_per_year)

        sharpe = self._safe_division(excess_return.mean() * self.periods_per_year, annualized_vol)
        sortino = self._safe_division(excess_return.mean() * self.periods_per_year, downside_vol)

        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdowns = cumulative / running_max - 1
        max_drawdown = drawdowns.min()
        calmar = self._safe_division(cagr, abs(max_drawdown))

        information_ratio = None
        if benchmark_returns is not None:
            info_ratio = self._information_ratio(returns, benchmark_returns)
            information_ratio = info_ratio if np.isfinite(info_ratio) else None

        return PerformanceMetrics(
            total_return=float(total_return),
            cagr=float(cagr),
            annualized_vol=float(annualized_vol),
            sharpe=float(sharpe),
            sortino=float(sortino),
            max_drawdown=float(max_drawdown),
            calmar=float(calmar),
            information_ratio=information_ratio,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def _risk_free_periodic(self) -> float:
        return (1 + self.risk_free_rate) ** (1 / self.periods_per_year) - 1

    def _information_ratio(self, returns: pd.Series, benchmark_returns: pd.Series) -> float:
        combined = returns.align(benchmark_returns, join="inner")
        portfolio_ret = combined[0]
        benchmark_ret = combined[1]
        active = portfolio_ret - benchmark_ret
        tracking_error = active.std() * np.sqrt(self.periods_per_year)
        active_return = active.mean() * self.periods_per_year
        return self._safe_division(active_return, tracking_error)

    @staticmethod
    def _safe_division(numerator: float, denominator: float) -> float:
        if denominator == 0:
            return float("nan")
        return numerator / denominator


def annualized_return(returns: Iterable[float], periods_per_year: int = 252) -> float:
    series = pd.Series(returns).dropna()
    if series.empty:
        raise ValueError("Retornos insuficientes")
    return (1 + series.mean()) ** periods_per_year - 1


def annualized_volatility(returns: Iterable[float], periods_per_year: int = 252) -> float:
    series = pd.Series(returns).dropna()
    if series.empty:
        raise ValueError("Retornos insuficientes")
    return series.std() * np.sqrt(periods_per_year)

