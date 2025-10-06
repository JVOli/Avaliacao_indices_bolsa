from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from numpy import multiply
import pandas as pd
import yfinance as yf

from .config import get_paths, load_grupos


@dataclass
class DownloadResult:
    symbol: str
    rows: int
    path: Path


def ensure_prices_dir() -> Path:
    paths = get_paths()
    prices_dir = paths.data_dir / "prices"
    prices_dir.mkdir(parents=True, exist_ok=True)
    return prices_dir


def to_yahoo_symbol(sym: str, overrides: Optional[Dict[str, str]] = None) -> str:
    s = sym.upper().strip()
    if overrides and s in overrides:
        return overrides[s]
    # Índices conhecidos
    if s == "IBOV":
        return "^BVSP"
    # Heurística: ações B3 com sufixo .SA caso não haja sufixo
    if s.startswith("^"):
        return s
    if "." not in s:
        return f"{s}.SA"
    return s


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    out = df.rename(columns=rename)
    # garante ordem
    cols = [c for c in ["open", "high", "low", "close", "adj_close", "volume"] if c in out.columns]
    return out[cols]


def download_prices(
    symbols: Iterable[str],
    start: str = "2014-01-01",
    end: Optional[str] = None,
    interval: str = "1d",
    auto_adjust: bool = True,
    overrides: Optional[Dict[str, str]] = None,
) -> List[DownloadResult]:
    prices_dir = ensure_prices_dir()
    results: List[DownloadResult] = []
    for sym in symbols:
        ysym = to_yahoo_symbol(sym, overrides)
        df = yf.download(ysym, start=start, end=end, interval=interval, auto_adjust=auto_adjust, progress=False, multi_level_index=False)
        if df.empty:
            # tenta sem auto_adjust
            df = yf.download(ysym, start=start, end=end, interval=interval, auto_adjust=False, progress=False, multi_level_index=False)
        if df.empty:
            # nothing fetched
            results.append(DownloadResult(symbol=sym, rows=0, path=prices_dir / f"{sym.upper()}.csv"))
            continue
        df.index.name = "date"
        df = normalize_columns(df)
        out_path = prices_dir / f"{sym.upper()}.csv"
        df.to_csv(out_path)
        results.append(DownloadResult(symbol=sym, rows=len(df), path=out_path))
    return results


def download_by_groups(groups: Optional[List[str]] = None, **kwargs) -> List[DownloadResult]:
    grupos = load_grupos()
    if groups:
        symbols: List[str] = []
        for g in groups:
            symbols.extend(grupos.get(g, []))
    else:
        # todos
        symbols = sorted({s for arr in grupos.values() for s in arr})
    return download_prices(symbols, **kwargs)


def cli():
    parser = argparse.ArgumentParser(description="Baixa cotações via yfinance e salva CSVs em data/prices/")
    parser.add_argument("--symbols", nargs="*", help="Lista de símbolos (ex: PETR4 VALE3 IBOV)")
    parser.add_argument("--groups", nargs="*", help="Baixar por grupos de grupos.json (ex: amplos setoriais)")
    parser.add_argument("--start", default="2014-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--no-auto-adjust", action="store_true", help="Não ajustar preços por proventos")
    args = parser.parse_args()

    auto_adjust = not args.no_auto_adjust

    results: List[DownloadResult] = []
    if args.symbols:
        results = download_prices(args.symbols, start=args.start, end=args.end, interval=args.interval, auto_adjust=auto_adjust)
    else:
        results = download_by_groups(groups=args.groups, start=args.start, end=args.end, interval=args.interval, auto_adjust=auto_adjust)

    ok = [r for r in results if r.rows > 0]
    ko = [r for r in results if r.rows == 0]
    print(f"Baixados: {len(ok)} | Vazios: {len(ko)}")
    for r in ok:
        print(f"  {r.symbol}: {r.rows} linhas -> {r.path}")
    if ko:
        print("Não retornou dados:")
        for r in ko:
            print(f"  {r.symbol}")


if __name__ == "__main__":
    cli()


