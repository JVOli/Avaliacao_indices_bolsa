#!/usr/bin/env python3
"""
Script principal: roda o pipeline de análises descrito no README.
"""
from pathlib import Path
import json

from src.analytics import run_all_groups, run_core_analysis, plot_risk_return_for_indices
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

    # Scatter risco-retorno (componentes vs índice) para todos os índices
    print("Gerando scatters risco-retorno (índice vs componentes)...")
    plot_risk_return_for_indices(start="2014-01-01")
    print("Scatters salvos em avaliacao_indices/outputs/*_risk_return_scatter.png")


if __name__ == "__main__":
    main()
