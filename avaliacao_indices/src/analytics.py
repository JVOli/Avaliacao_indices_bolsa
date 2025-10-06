from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
import yfinance as yf

from .config import get_paths, load_grupos
from .data_io import load_prices_for_symbols, load_cdi_series, load_index_composition
from .metrics import (
    Summary,
    align_excess_returns,
    infer_periods_per_year,
    summarize_series,
    annualize_return,
    annualize_volatility,
)
from .seasonality import seasonality_by_month, seasonality_by_weekday
from .extremes import impact_of_extremes, event_study_after_extreme
from .plots import plot_cum_returns, plot_drawdown, plot_bar_metrics, plot_heatmap_monthly, plot_extremes_curves, plot_risk_return_scatter
from .download_yf import to_yahoo_symbol


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

    # Sazonalidade e extremos para todos os símbolos
    for sym in excess.columns:
        s = excess[sym].dropna()
        by_month = seasonality_by_month(s)
        by_weekday = seasonality_by_weekday(s)
        by_month.to_csv(out_dir / f"{sym}_season_month.csv")
        by_weekday.to_csv(out_dir / f"{sym}_season_weekday.csv")
        plot_heatmap_monthly(by_month[["avg"]], f"Sazonalidade mensal - {sym}", out_dir / f"{sym}_season_month.png")

        ext = impact_of_extremes(s, ns=[1, 5])
        ext.to_csv(out_dir / f"{sym}_extremes.csv", index=False)
        # Plots comparando base vs remoção de melhores/piores dias
        for n in [1, 5]:
            plot_extremes_curves(s, n, f"Extremos (n={n}) - {sym}", out_dir / f"{sym}_extremes_n{n}.png")

        evt = event_study_after_extreme(s)
        evt.to_csv(out_dir / f"{sym}_event_study.csv", index=False)

    return results


def run_all_groups() -> Dict[str, Dict]:
    grupos = load_grupos()
    outputs: Dict[str, Dict] = {}
    for name, symbols in grupos.items():
        outputs[name] = run_core_analysis(symbols)
    return outputs


def _extract_prices_from_yf(df: pd.DataFrame) -> pd.DataFrame:
    # aceita retorno do yf.download para múltiplos símbolos (MultiIndex nas colunas)
    if isinstance(df.columns, pd.MultiIndex):
        level0 = set(df.columns.get_level_values(0))
        key = "Adj Close" if "Adj Close" in level0 else ("Close" if "Close" in level0 else None)
        if key is None:
            return pd.DataFrame()
        prices = df[key].copy()
        prices.columns = [str(c).upper() for c in prices.columns]
        return prices
    # único símbolo
    cols = [c for c in ["Adj Close", "Close"] if c in df.columns]
    if not cols:
        return pd.DataFrame()
    prices = df[cols[0]].to_frame()
    prices.columns = ["SINGLE"]
    return prices


def build_components_risk_return(index_symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> Optional[Dict]:
    comps = load_index_composition(index_symbol)
    if not comps:
        return None
    b3_syms = [c.get("symb", "").strip() for c in comps if c.get("symb")]
    if not b3_syms:
        return None
    yf_syms = [to_yahoo_symbol(s) for s in b3_syms]
    df = yf.download(yf_syms, start=start, end=end, auto_adjust=True, progress=False)
    prices = _extract_prices_from_yf(df)
    if prices.empty:
        return None
    # Mapear pesos da composição (normalizados)
    w_map = {}
    for c in comps:
        sym_b3 = c.get("symb")
        if not sym_b3:
            continue
        w_map[to_yahoo_symbol(sym_b3).upper()] = float(c.get("indxCmpnPctg", 0.0))
    weights = pd.Series(w_map, dtype=float)
    if weights.sum() > 0:
        weights = weights / weights.sum()
    # Retornos
    returns = prices.pct_change().dropna(how="all")
    # Estatísticas por componente
    stats_rows: List[Dict] = []
    for col in returns.columns:
        s = returns[col].dropna()
        if s.empty:
            continue
        stats_rows.append({
            "symbol": col,
            "ann_ret": annualize_return(s),
            "ann_vol": annualize_volatility(s),
        })
    components_stats = pd.DataFrame(stats_rows)
    if components_stats.empty:
        return None
    # Ponto do índice (carteira estática com pesos atuais)
    w = weights.reindex(returns.columns).fillna(0.0)
    idx_ret_series = (returns * w).sum(axis=1)
    index_ret = annualize_return(idx_ret_series)
    index_vol = annualize_volatility(idx_ret_series)
    return {
        "components_stats": components_stats,
        "index_ret": float(index_ret),
        "index_vol": float(index_vol),
    }


def plot_risk_return_for_indices(start: Optional[str] = None, end: Optional[str] = None) -> None:
    paths = get_paths()
    out_dir = paths.output_dir
    grupos = load_grupos()
    all_symbols = sorted({s for arr in grupos.values() for s in arr})
    for sym in all_symbols:
        rr = build_components_risk_return(sym, start=start, end=end)
        if rr is None:
            continue
        df_stats: pd.DataFrame = rr["components_stats"]
        plot_risk_return_scatter(
            df_stats,
            index_name=sym,
            index_ret=rr["index_ret"],
            index_vol=rr["index_vol"],
            title=f"Risco vs Retorno - {sym} (componentes vs índice)",
            outpath=out_dir / f"{sym}_risk_return_scatter.png",
        )


