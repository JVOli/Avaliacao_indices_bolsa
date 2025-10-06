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
    Placeholder para carregar séries de preços/índices caso existam arquivos com histórico.
    No momento, os arquivos presentes contêm composição teórica atual. Esta função retorna
    um DataFrame vazio até que uma fonte de históricos seja definida.
    """
    return pd.DataFrame()


def load_cdi_series() -> pd.Series:
    """
    Carrega a série de CDI diária caso exista fonte local; retorna vazia como stub por ora.
    """
    return pd.Series(dtype=float)


def load_prices_for_symbols(symbols: Iterable[str]) -> PriceBundle:
    # Stub de agregação; quando históricos forem adicionados, montar DataFrame com colunas por símbolo
    frames: List[pd.Series] = []
    metadata: Dict[str, Dict] = {}
    for sym in symbols:
        comp = load_index_composition(sym)
        metadata[sym] = {"num_constituents": len(comp)}
    if frames:
        prices = pd.concat(frames, axis=1)
    else:
        prices = pd.DataFrame()
    return PriceBundle(prices=prices, metadata=metadata)


