"""Funções e classes utilitárias para leitura dos dados históricos.

Organiza o carregamento de preços (CSV) e metadados (JSON) presentes em
`avaliacao_indices/data`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data"


class DataNotFoundError(FileNotFoundError):
    """Erro disparado quando um recurso solicitado não é encontrado."""


@dataclass(slots=True)
class IndexMetadata:
    """Metadados básicos de um índice."""

    symbol: str
    description: str
    constituents: Dict[str, float]


class DataLoader:
    """Carrega dados de preços e metadados dos índices."""

    def __init__(self, data_dir: Optional[Path | str] = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        if not self.data_dir.exists():
            raise DataNotFoundError(f"Diretório de dados inexistente: {self.data_dir}")

    # ------------------------------------------------------------------
    # Preços
    # ------------------------------------------------------------------
    def list_available_indices(self) -> Iterable[str]:
        """Lista os códigos de índices com dados de preços disponíveis."""

        prices_dir = self._prices_dir
        if not prices_dir.exists():
            return []

        return sorted(path.stem for path in prices_dir.glob("*.csv"))

    def load_price_history(self, symbol: str, *, parse_dates: bool = True) -> pd.DataFrame:
        """Carrega histórico diário de preços para um índice.

        Espera um arquivo CSV com colunas padrão exportadas pelo investpy ou
        fonte equivalente: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`,
        `Currency`.
        """

        csv_path = self._prices_dir / f"{symbol.upper()}.csv"
        if not csv_path.exists():
            raise DataNotFoundError(f"Arquivo de preços não encontrado: {csv_path}")

        df = pd.read_csv(csv_path)
        if parse_dates and "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], utc=True)
            df = df.set_index("Date").sort_index()
        return df

    # ------------------------------------------------------------------
    # Metadados
    # ------------------------------------------------------------------
    def load_metadata(self, symbol: str) -> IndexMetadata:
        """Carrega metadados (composição) para um índice."""

        json_path = self.data_dir / f"cotacoes_{symbol.upper()}.json"
        if not json_path.exists():
            raise DataNotFoundError(f"Metadados não encontrados: {json_path}")

        raw = pd.read_json(json_path)
        index_info = raw.get("Index", {})
        constituents = {
            item["symb"]: item["indxCmpnPctg"] / 100
            for item in raw.get("UnderlyingList", [])
            if "symb" in item and "indxCmpnPctg" in item
        }

        return IndexMetadata(
            symbol=index_info.get("symbol", symbol.upper()),
            description=index_info.get("description", ""),
            constituents=constituents,
        )

    def load_group_mapping(self) -> Dict[str, str]:
        """Carrega o mapeamento de índices para grupos de análise."""

        json_path = self.data_dir / "grupos.json"
        if not json_path.exists():
            raise DataNotFoundError(f"Arquivo de grupos não encontrado: {json_path}")

        data = pd.read_json(json_path)
        if isinstance(data, pd.DataFrame):
            return dict(zip(data["index"], data["group"]))
        if isinstance(data, dict):
            return {item["index"]: item["group"] for item in data.get("grupos", [])}

        raise ValueError("Formato de grupos.json não suportado")

    # ------------------------------------------------------------------
    # Utilitários internos
    # ------------------------------------------------------------------
    @property
    def _prices_dir(self) -> Path:
        return self.data_dir / "prices"

