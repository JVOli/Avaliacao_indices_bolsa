from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import yfinance as yf

from .config import get_paths, load_grupos
from .data_io import load_index_composition
from .download_yf import to_yahoo_symbol, normalize_columns


@dataclass
class DownloadResult:
    index_symbol: str
    b3_symbol: str
    yahoo_symbol: str
    rows: int
    path: Path


def ensure_prices_dir() -> Path:
    paths = get_paths()
    prices_dir = paths.data_dir / "prices"
    prices_dir.mkdir(parents=True, exist_ok=True)
    return prices_dir


def download_stock(sym_b3: str, start: Optional[str], end: Optional[str], interval: str, auto_adjust: bool) -> pd.DataFrame:
    ysym = to_yahoo_symbol(sym_b3)
    df = yf.download(ysym, start=start, end=end, interval=interval, auto_adjust=auto_adjust, progress=False, multi_level_index=False)
    if df.empty:
        df = yf.download(ysym, start=start, end=end, interval=interval, auto_adjust=not auto_adjust, progress=False, multi_level_index=False)
    if df.empty:
        return pd.DataFrame()
    df.index.name = "date"
    return normalize_columns(df)


def list_indices_from_grupos(selected_indices: Optional[List[str]] = None) -> List[str]:
    grupos = load_grupos()
    all_syms = sorted({s for arr in grupos.values() for s in arr})
    if selected_indices:
        selected_set = {s.upper() for s in selected_indices}
        return [s for s in all_syms if s.upper() in selected_set]
    return all_syms


def download_components_for_index(index_symbol: str, start: Optional[str], end: Optional[str], interval: str, auto_adjust: bool, skip_existing: bool) -> List[DownloadResult]:
    comps = load_index_composition(index_symbol)
    if not comps:
        return []
    prices_dir = ensure_prices_dir()
    results: List[DownloadResult] = []
    for comp in comps:
        b3 = comp.get("symb")
        if not b3:
            continue
        out_path = prices_dir / f"{b3.upper()}.csv"
        if skip_existing and out_path.exists():
            # conta as linhas para report
            try:
                nrows = sum(1 for _ in open(out_path, "r", encoding="utf-8")) - 1
            except Exception:
                nrows = 0
            results.append(DownloadResult(index_symbol=index_symbol, b3_symbol=b3, yahoo_symbol=to_yahoo_symbol(b3), rows=max(nrows, 0), path=out_path))
            continue
        df = download_stock(b3, start=start, end=end, interval=interval, auto_adjust=auto_adjust)
        if df.empty:
            results.append(DownloadResult(index_symbol=index_symbol, b3_symbol=b3, yahoo_symbol=to_yahoo_symbol(b3), rows=0, path=out_path))
            continue
        df.to_csv(out_path)
        results.append(DownloadResult(index_symbol=index_symbol, b3_symbol=b3, yahoo_symbol=to_yahoo_symbol(b3), rows=len(df), path=out_path))
    return results


def download_components(indices: Optional[List[str]] = None, start: Optional[str] = None, end: Optional[str] = None, interval: str = "1d", auto_adjust: bool = True, skip_existing: bool = True) -> List[DownloadResult]:
    indices_list = list_indices_from_grupos(indices)
    all_results: List[DownloadResult] = []
    for idx in indices_list:
        res = download_components_for_index(idx, start=start, end=end, interval=interval, auto_adjust=auto_adjust, skip_existing=skip_existing)
        all_results.extend(res)
    return all_results


def cli():
    parser = argparse.ArgumentParser(description="Baixa históricos das ações componentes de cada índice (yfinance) e salva CSVs em data/prices/")
    parser.add_argument("--indices", nargs="*", help="Lista de índices (ex: IBOV IFNC IDIV). Se omitido, usa todos de grupos.json")
    parser.add_argument("--start", default="2014-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--no-auto-adjust", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true", help="Rebaixa e sobrescreve CSVs existentes")
    args = parser.parse_args()

    auto_adjust = not args.no_auto_adjust
    skip_existing = not args.no_skip_existing

    results = download_components(indices=args.indices, start=args.start, end=args.end, interval=args.interval, auto_adjust=auto_adjust, skip_existing=skip_existing)

    # sumariza por índice
    by_index: Dict[str, Tuple[int, int]] = {}
    for r in results:
        ok, ko = by_index.get(r.index_symbol, (0, 0))
        if r.rows > 0:
            ok += 1
        else:
            ko += 1
        by_index[r.index_symbol] = (ok, ko)
    print("Resumo por índice (baixados | vazios):")
    for idx, (ok, ko) in sorted(by_index.items()):
        print(f"  {idx}: {ok} | {ko}")

    total_ok = sum(1 for r in results if r.rows > 0)
    total_ko = sum(1 for r in results if r.rows == 0)
    print(f"Total: baixados={total_ok} | vazios={total_ko}")


if __name__ == "__main__":
    cli()


