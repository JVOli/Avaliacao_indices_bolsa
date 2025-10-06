from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd

from .config import get_paths, load_grupos
from .data_io import load_prices_for_symbols, load_cdi_series
from .metrics import (
    Summary,
    align_excess_returns,
    infer_periods_per_year,
    summarize_series,
)
from .seasonality import seasonality_by_month, seasonality_by_weekday
from .extremes import impact_of_extremes, event_study_after_extreme
from .plots import plot_cum_returns, plot_drawdown, plot_bar_metrics, plot_heatmap_monthly


def run_core_analysis(symbols: List[str]) -> Dict:
    paths = get_paths()
    out_dir = paths.output_dir
    bundle = load_prices_for_symbols(symbols)
    cdi = load_cdi_series()

    results: Dict = {"symbols": symbols, "metadata": bundle.metadata, "summaries": {}}

    if bundle.prices.empty:
        # Sem séries de preço; apenas salvar metadados e instruções
        (out_dir / "README_outputs.txt").write_text(
            "Sem séries históricas de preços. Adicione CSVs em avaliacao_indices/data com colunas date, close.",
            encoding="utf-8",
        )
        return results

    # Retornos simples diários
    returns = bundle.prices.pct_change().dropna(how="all")

    # Excesso ao CDI
    excess = align_excess_returns(returns, cdi)

    # Métricas básicas
    summaries: Dict[str, Summary] = {}
    for sym in excess.columns:
        s = excess[sym].dropna()
        summaries[sym] = summarize_series(s)
        # plots
        plot_drawdown(s, f"Drawdown - {sym}", out_dir / f"{sym}_drawdown.png")

    results["summaries"] = {k: vars(v) for k, v in summaries.items()}

    # Retorno acumulado
    plot_cum_returns(excess, "Retornos acumulados (excesso ao CDI)", out_dir / "cum_returns_excess.png")

    # Sazonalidade e extremos para o primeiro símbolo como exemplo
    first = excess.columns[0]
    s = excess[first].dropna()
    by_month = seasonality_by_month(s)
    by_weekday = seasonality_by_weekday(s)
    by_month.to_csv(out_dir / f"{first}_season_month.csv")
    by_weekday.to_csv(out_dir / f"{first}_season_weekday.csv")
    plot_heatmap_monthly(by_month[["avg"]], f"Sazonalidade mensal - {first}", out_dir / f"{first}_season_month.png")

    ext = impact_of_extremes(s, ns=[5, 10, 20])
    ext.to_csv(out_dir / f"{first}_extremes.csv", index=False)
    evt = event_study_after_extreme(s)
    evt.to_csv(out_dir / f"{first}_event_study.csv", index=False)

    return results


def run_all_groups() -> Dict[str, Dict]:
    grupos = load_grupos()
    outputs: Dict[str, Dict] = {}
    for name, symbols in grupos.items():
        outputs[name] = run_core_analysis(symbols)
    return outputs


