"""Pacote principal para análise dos índices da B3.

Este módulo expõe classes e funções utilitárias para carregar dados
históricos, calcular métricas de risco-retorno e avaliar concentração
dos índices disponibilizados em `avaliacao_indices/data`.
"""

from .data_loader import DataLoader
from .performance import PerformanceAnalyzer, PerformanceMetrics
from .concentration import (
    compute_hhi,
    effective_number_of_assets,
    top_n_concentration,
    diversification_ratio,
)

__all__ = [
    "DataLoader",
    "PerformanceAnalyzer",
    "PerformanceMetrics",
    "compute_hhi",
    "effective_number_of_assets",
    "top_n_concentration",
    "diversification_ratio",
]

