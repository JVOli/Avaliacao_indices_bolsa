from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from .config import get_paths


@dataclass
class PriceBundle:
    prices: pd.DataFrame  # index=datetime, columns=symbols (level: close)
    metadata: Dict[str, Dict]


def _read_index_quotes(json_path: Path) -> Dict:
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_index_composition(symbol: str) -> List[Dict]:
    # Carrega a composição teórica mais recente (quando disponível nos arquivos locais)
    paths = get_paths()
    json_path = paths.data_dir / f"cotacoes_{symbol.upper()}.json"
    if not json_path.exists():
        return []
    payload = _read_index_quotes(json_path)
    return payload.get("UnderlyingList", [])


def load_index_price_series(symbol: str) -> pd.DataFrame:
    """
    Carrega a série de preços do símbolo a partir de CSV salvo em data/prices/{SYMBOL}.csv
    Espera colunas: date, close (ou adj_close). Retorna DataFrame com coluna 'close'.
    """
    paths = get_paths()
    csv_path = paths.data_dir / "prices" / f"{symbol.upper()}.csv"
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(csv_path, parse_dates=["Date"])  # index será setado abaixo
    df.columns = df.columns.str.lower()
    df = df.set_index("date").sort_index()
    if "close" not in df.columns and "adj_close" in df.columns:
        df["close"] = df["adj_close"]
    if "close" not in df.columns:
        return pd.DataFrame()
    return df[["close"]]


def load_cdi_series() -> pd.Series:
    """
    Carrega a série de CDI diária caso exista fonte local; retorna vazia como stub por ora.
    """
    return pd.Series(dtype=float)


def load_prices_for_symbols(symbols: Iterable[str]) -> PriceBundle:
    frames: List[pd.Series] = []
    metadata: Dict[str, Dict] = {}
    for sym in symbols:
        comp = load_index_composition(sym)
        metadata[sym] = {"num_constituents": len(comp)}
        df = load_index_price_series(sym)
        if not df.empty:
            s = df["close"].rename(sym.upper())
            frames.append(s)
    prices = pd.concat(frames, axis=1) if frames else pd.DataFrame()
    return PriceBundle(prices=prices, metadata=metadata)


