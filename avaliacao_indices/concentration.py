"""Métricas de concentração de portfólio."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np


def _normalize_weights(weights: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(weights), dtype=float)
    if arr.size == 0:
        raise ValueError("Nenhum peso fornecido")
    total = arr.sum()
    if total <= 0:
        raise ValueError("Soma dos pesos deve ser positiva")
    return arr / total


def compute_hhi(weights: Iterable[float]) -> float:
    """Calcula o índice Herfindahl-Hirschman (HHI)."""

    normalized = _normalize_weights(weights)
    return float(np.sum(normalized**2))


def effective_number_of_assets(weights: Iterable[float]) -> float:
    """Número efetivo de ativos (1 / HHI)."""

    hhi = compute_hhi(weights)
    if hhi == 0:
        return float("inf")
    return float(1 / hhi)


def top_n_concentration(weights: Sequence[float], n: int = 10) -> float:
    """Soma dos N maiores pesos."""

    if n <= 0:
        raise ValueError("n deve ser positivo")
    normalized = _normalize_weights(weights)
    return float(np.sort(normalized)[-n:].sum())


def diversification_ratio(weights: Iterable[float], volatilities: Iterable[float]) -> float:
    """Diversification Ratio = Σ(wᵢ σᵢ) / σ_portfólio."""

    weights_arr = _normalize_weights(weights)
    vols_arr = np.asarray(list(volatilities), dtype=float)
    if vols_arr.size != weights_arr.size:
        raise ValueError("Pesos e volatilidades precisam ter o mesmo tamanho")
    if np.any(vols_arr < 0):
        raise ValueError("Volatilidades devem ser não negativas")

    numerator = float(np.sum(weights_arr * vols_arr))

    cov_diag = np.diag(vols_arr**2)
    portfolio_variance = weights_arr @ cov_diag @ weights_arr
    portfolio_vol = np.sqrt(portfolio_variance)
    if portfolio_vol == 0:
        return float("nan")

    return numerator / portfolio_vol

