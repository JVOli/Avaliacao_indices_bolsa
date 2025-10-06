
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
from yahooquery import Ticker

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
    if s == "IBOV":
        return "^BVSP"
    if s.startswith("^"):
        return s
    if "." not in s:
        return f"{s}.SA"
    return s


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "adjclose": "adj_close",
        "volume": "volume",
    }
    out = df.rename(columns=rename)
    cols = [c for c in ["open", "high", "low", "close", "adj_close", "volume"] if c in out.columns]
    return out[cols]


def download_prices(
    symbols: Iterable[str],
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: str = "1d",
    adj_ohlc: bool = True,
    overrides: Optional[Dict[str, str]] = None,
) -> List[DownloadResult]:
    prices_dir = ensure_prices_dir()
    mapped = [to_yahoo_symbol(s, overrides) for s in symbols]
    t = Ticker(mapped, asynchronous=True)
    hist = t.history(start=start, end=end, interval=interval, adj_ohlc=adj_ohlc)
    results: List[DownloadResult] = []
    if isinstance(hist, dict) or hist is None:
        # erro ou sem dados
        for s in symbols:
            results.append(DownloadResult(symbol=s, rows=0, path=prices_dir / f"{s.upper()}.csv"))
        return results
    # DataFrame: pode vir com MultiIndex (symbol, date) ou index simples para único símbolo
    if "symbol" not in hist.columns:
        # único símbolo
        sym = symbols[0]
        df = hist.copy()
        if not isinstance(df.index, pd.DatetimeIndex) and "date" in df.columns:
            df = df.set_index("date")
        df.index.name = "date"
        df = normalize_columns(df)
        out_path = prices_dir / f"{sym.upper()}.csv"
        df.to_csv(out_path)
        results.append(DownloadResult(symbol=sym, rows=len(df), path=out_path))
        return results

    # múltiplos símbolos
    # se index não tem 'date', tentar coluna
    if not isinstance(hist.index, pd.MultiIndex) and "date" in hist.columns:
        # já vem com coluna 'symbol'
        pass
    # garantir coluna 'date'
    if isinstance(hist.index, pd.MultiIndex):
        if hist.index.names == ["symbol", "date"]:
            hist = hist.reset_index()
        else:
            hist = hist.reset_index()

    for sym, g in hist.groupby("symbol"):
        df = g.copy()
        if "date" in df.columns:
            df = df.set_index("date")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.index.name = "date"
        df = normalize_columns(df)
        # salvar com nome original requisitado, se mapeado de volta
        # tenta achar original correspondente
        out_sym = None
        s_map = {to_yahoo_symbol(s): s for s in symbols}
        out_sym = s_map.get(sym, sym)
        out_path = prices_dir / f"{out_sym.upper()}.csv"
        df.to_csv(out_path)
        results.append(DownloadResult(symbol=out_sym, rows=len(df), path=out_path))

    # garantir que símbolos sem dado constem
    done = {r.symbol.upper() for r in results}
    for s in symbols:
        if s.upper() not in done:
            results.append(DownloadResult(symbol=s, rows=0, path=prices_dir / f"{s.upper()}.csv"))

    return results


def download_by_groups(groups: Optional[List[str]] = None, **kwargs) -> List[DownloadResult]:
    grupos = load_grupos()
    if groups:
        symbols: List[str] = []
        for g in groups:
            symbols.extend(grupos.get(g, []))
    else:
        symbols = sorted({s for arr in grupos.values() for s in arr})
    return download_prices(symbols, **kwargs)


def cli():
    parser = argparse.ArgumentParser(description="Baixa cotações via yahooquery e salva CSVs em data/prices/")
    parser.add_argument("--symbols", nargs="*", help="Lista de símbolos (ex: PETR4 VALE3 IBOV)")
    parser.add_argument("--groups", nargs="*", help="Baixar por grupos de grupos.json (ex: amplos setoriais)")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--no-adj-ohlc", action="store_true", help="Não ajustar OHLC por proventos")
    args = parser.parse_args()

    adj_ohlc = not args.no_adj_ohlc

    if args.symbols:
        results = download_prices(args.symbols, start=args.start, end=args.end, interval=args.interval, adj_ohlc=adj_ohlc)
    else:
        results = download_by_groups(groups=args.groups, start=args.start, end=args.end, interval=args.interval, adj_ohlc=adj_ohlc)

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


