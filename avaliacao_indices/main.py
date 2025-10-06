#!/usr/bin/env python3
"""
Script principal: roda o pipeline de análises descrito no README.
"""
from pathlib import Path
import json

from src.analytics import run_all_groups, run_core_analysis
from src.config import load_grupos


def main():
    grupos = load_grupos()
    print("Executando análise para todos os grupos definidos em grupos.json...")
    outputs = run_all_groups()
    # salvar um resumo em JSON
    package_root = Path(__file__).parent
    out_json = package_root / "outputs" / "summary.json"
    out_json.parent.mkdir(exist_ok=True)
    out_json.write_text(json.dumps(outputs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Resumo salvo em {out_json}")


if __name__ == "__main__":
    main()
