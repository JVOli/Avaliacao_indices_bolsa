from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def plot_cum_returns(r: pd.DataFrame, title: str, outpath: Path) -> None:
    ensure_dir(outpath.parent)
    wealth = (1 + r).cumprod()
    ax = wealth.plot(figsize=(10, 5))
    ax.set_title(title)
    ax.set_ylabel("Índice de riqueza (base 1.0)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_drawdown(r: pd.Series, title: str, outpath: Path) -> None:
    ensure_dir(outpath.parent)
    wealth = (1 + r).cumprod()
    peak = wealth.cummax()
    dd = wealth / peak - 1
    ax = dd.plot.area(figsize=(10, 3), color="#d9534f", alpha=0.6)
    ax.set_title(title)
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_bar_metrics(df_metrics: pd.DataFrame, title: str, outpath: Path) -> None:
    ensure_dir(outpath.parent)
    ax = df_metrics.plot(kind="bar", figsize=(10, 5))
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_heatmap_monthly(means_by_month: pd.DataFrame, title: str, outpath: Path) -> None:
    ensure_dir(outpath.parent)
    plt.figure(figsize=(8, 4))
    data = means_by_month.reindex(index=range(1, 13))
    plt.imshow(data.values.reshape(-1, 1), aspect="auto", cmap="RdYlGn", vmin=data.min().min(), vmax=data.max().max())
    plt.yticks(range(12), [str(i) for i in range(1, 13)])
    plt.xticks([0], ["Retorno médio"])
    plt.title(title)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


