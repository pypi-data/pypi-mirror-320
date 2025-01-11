import json
import importlib
from mapafiscal.interfaces.repositorio_interface import RepositorioInterface


def importar_tabelas(filename: str, repositorio: RepositorioInterface):

    def obter_classe_item(classe_item: str):
        clazz_module = classe_item.rsplit('.', 1) [0] 
        clazz_name = classe_item.rsplit('.', 1) [1] 
        # Importar o módulo 
        module_instance = importlib.import_module(clazz_module) 
        # Obter a classe do módulo 
        return getattr(module_instance, clazz_name)

    try:     
        try:   
            with open(filename, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except json.JSONDecodeError:
            print(f"Erro ao carregar o arquivo JSON: {filename}")
        except FileNotFoundError:
            print(f"Arquivo {filename} não encontrado.")

        tabela = dados.get("tabela", {})
        if not tabela:
            raise ValueError(f"Nenhuma tabela encontrada no arquivo {filename}.")

        tabela_nome = tabela.get("nome")
        classe_item = tabela.get("classe_item", None)
        if classe_item is None:
            raise ValueError(f"Elemento 'classe_item' não encontrado na tabela {tabela_nome}.")
        
        print(f"Importando dados da tabela {tabela_nome} para o repositório...")

        itens = tabela.get("itens", [])
        if not itens:
            raise ValueError(f"Nenhum dado encontrado na tabela {tabela_nome}")

        for item in itens:
            clazz_type = obter_classe_item(classe_item)
            obj = clazz_type(**item)  
            repositorio.adicionar(obj, clazz_type)

        print("Dados importados com sucesso para o repositório!")

    except Exception as e:
        print(f"Erro inesperado: {e}")

    

    



