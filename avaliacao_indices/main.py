#!/usr/bin/env python3
"""
Script principal para buscar e exibir dados de índices da B3.
"""
import json
from pathlib import Path
import time

from src.fetch_indexes import BuscadorIndices


def exibir_composicao_indice(indice: str, forcar_atualizacao: bool = False):
    """
    Busca e exibe a composição de um índice da B3.
    
    Args:
        indice: Código do índice (ex: IBOV, IFIX, IDIV, SMLL)
        forcar_atualizacao: Se True, força a busca na API
    """
    print("=" * 70)
    print(f"COMPOSIÇÃO DO ÍNDICE: {indice}")
    print("=" * 70)
    
    buscador = BuscadorIndices(indice=indice)
    dados = buscador.obter_dados(forcar_atualizacao=forcar_atualizacao)
    
    if not dados or 'Index' not in dados:
        print(f"\nErro: Não foi possível obter dados do índice {indice}")
        return
    
    print(f"\nÍndice: {dados['Index'].get('symbol', 'N/A')}")
    print(f"Descrição: {dados['Index'].get('description', 'N/A')}")
    
    ativos = dados.get('UnderlyingList', [])
    print(f"Total de ativos: {len(ativos)}")
    
    if 'Msg' in dados and 'dtTm' in dados['Msg']:
        print(f"Última atualização: {dados['Msg']['dtTm']}")
    
    if ativos:
        print(f"\nTop 10 Maiores Participações:")
        print("-" * 70)
        
        ativos_ordenados = sorted(
            ativos, 
            key=lambda x: float(x.get('indxCmpnPctg', 0)), 
            reverse=True
        )[:10]
        
        for i, ativo in enumerate(ativos_ordenados, 1):
            simbolo = ativo.get('symb', 'N/A')
            descricao = ativo.get('desc', 'N/A')
            participacao = float(ativo.get('indxCmpnPctg', 0))
            
            print(f"{i:2d}. {simbolo:8s} | {descricao:30s} | {participacao:6.2f}%")
    
    print("\n" + "=" * 70)


def main():
    """
    Função principal do script.
    """
    print("\nSistema de Consulta de Índices da B3")
    print("=" * 70)
    
    indices_disponiveis = json.load(open(Path(__file__).parent / "data" / "cotacoes_indices.json"))
    for index in indices_disponiveis["rows"]:
        print(f"  {index['symbol']:6s} - {index['description']}")

        exibir_composicao_indice(index["symbol"], forcar_atualizacao=False)
        time.sleep(5)

    print("\n" + "=" * 70)
    

if __name__ == "__main__":
    main()
