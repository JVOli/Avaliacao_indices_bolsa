#%%
import requests
import json
from pathlib import Path
from typing import Dict, Any


class BuscadorIndices:
    """
    Classe responsável por buscar e gerenciar dados de índices da B3.
    """
    
    def __init__(self, arquivo_json: str = "cotacoes_indices.json"):
        """
        Inicializa o buscador de índices.
        
        Args:
            arquivo_json: Nome do arquivo JSON para salvar/carregar os dados
        """
        # Obtém o diretório do script e define o caminho absoluto
        script_dir = Path(__file__).parent.parent
        self.data_dir = script_dir / "data"
        self.arquivo_json = self.data_dir / arquivo_json
        
        # URL da API da B3
        self.url = "https://www.b3.com.br/lumis/api/rest/cotacoes-indices/lumgetdata/list.json"
        
        # Headers para simular um navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-amplos/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        # Cria o diretório 'data' se não existir
        self.data_dir.mkdir(exist_ok=True)
        
        self.dados = None
    
    def arquivo_existe(self) -> bool:
        """
        Verifica se o arquivo JSON já existe localmente.
        
        Returns:
            True se o arquivo existe, False caso contrário
        """
        return self.arquivo_json.exists()
    
    def carregar_dados_locais(self) -> Dict[str, Any]:
        """
        Carrega os dados do arquivo JSON local.
        
        Returns:
            Dicionário com os dados carregados
        """
        print(f"Arquivo '{self.arquivo_json}' já existe. Carregando dados locais...")
        with open(self.arquivo_json, 'r', encoding='utf-8') as f:
            self.dados = json.load(f)
        return self.dados
    
    def buscar_dados_api(self) -> Dict[str, Any]:
        """
        Busca os dados da API da B3.
        
        Returns:
            Dicionário com os dados obtidos da API
        """
        print(f"Arquivo '{self.arquivo_json}' não encontrado. Fazendo requisição...")
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()  # Levanta exceção se houver erro HTTP
        self.dados = response.json()
        return self.dados
    
    def salvar_dados(self) -> None:
        """
        Salva os dados no arquivo JSON local.
        """
        if self.dados is None:
            raise ValueError("Não há dados para salvar. Execute buscar_dados_api() primeiro.")
        
        with open(self.arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)
        print(f"Dados salvos em '{self.arquivo_json}'")
    
    def obter_dados(self, forcar_atualizacao: bool = False) -> Dict[str, Any]:
        """
        Obtém os dados dos índices, seja do arquivo local ou da API.
        
        Args:
            forcar_atualizacao: Se True, força a busca na API mesmo que o arquivo exista
        
        Returns:
            Dicionário com os dados dos índices
        """
        if forcar_atualizacao or not self.arquivo_existe():
            self.buscar_dados_api()
            self.salvar_dados()
        else:
            self.carregar_dados_locais()
        
        return self.dados


# Exemplo de uso
if __name__ == "__main__":
    buscador = BuscadorIndices()
    dados = buscador.obter_dados()
    print(f"\nTotal de índices encontrados: {len(dados.get('results', []))}")

#%%
