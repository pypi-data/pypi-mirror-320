import json
from importlib import import_module
from mapafiscal.interfaces.repositorio_interface import RepositorioInterface
import shutil
from importlib.resources import files
from tqdm import tqdm

def copy_resource_file(package_path, nome_arquivo, destino):
    """
    Copia um arquivo de recurso para uma pasta local.
    
    Args:
        package_path (str): Caminho do pacote (ex.: 'mapafiscal.resources.tabelas').
        nome_arquivo (str): Nome do arquivo JSON a ser copiado.
        destino (str): Caminho local para onde o arquivo será copiado.
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado no pacote.
        Exception: Para outros erros gerais.
    """
    try:
        # Caminho completo do arquivo no pacote
        caminho_origem = files(package_path) / nome_arquivo

        # Copiar o arquivo para o destino
        shutil.copy(caminho_origem, destino)
        print(f"Arquivo '{nome_arquivo}' copiado para '{destino}'.")
    except FileNotFoundError:
        print(f"O arquivo '{nome_arquivo}' não foi encontrado em '{package_path}'.")
        raise
    except Exception as e:
        print(f"Erro ao copiar o arquivo: {e}")
        raise


def importar_tabelas(repositorio: RepositorioInterface, filename: str, encoding="utf-8"):

    def obter_classe_item(classe_item: str):
        clazz_module = classe_item.rsplit('.', 1) [0] 
        clazz_name = classe_item.rsplit('.', 1) [1] 
        # Importar o módulo 
        module_instance = import_module(clazz_module) 
        # Obter a classe do módulo 
        return getattr(module_instance, clazz_name)

    try:     
        try:   
            with open(filename, 'r', encoding=encoding) as f:
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
        
        itens = tabela.get("itens", [])
        if not itens:
            raise ValueError(f"Nenhum dado encontrado na tabela {tabela_nome}")

        for item in tqdm(itens, desc=f"Importando dados da tabela {tabela_nome}"):
            clazz_type = obter_classe_item(classe_item)
            obj = clazz_type(**item)  
            repositorio.adicionar(obj, clazz_type)

    except Exception as e:
        print(f"Erro inesperado: {e}")

def iniciar_repositorio(repositorio: RepositorioInterface, encoding="utf-8"):
    
    # Caminho completo do arquivo no pacote
    resources_path = files('mapafiscal.resources.tabelas')
    
    importar_tabelas(filename=resources_path / "tabela_aliquota_icms_estados_v1_001.json", 
                     repositorio=repositorio,
                     encoding=encoding)
    importar_tabelas(filename=resources_path / "tabela_aliquota_ipi_v1_001.json", 
                     repositorio=repositorio,
                     encoding=encoding)
    importar_tabelas(filename=resources_path / "tabela_operacoes_basicas_v1_001.json", 
                     repositorio=repositorio,
                     encoding=encoding)
    importar_tabelas(filename=resources_path / "tabela_pauta_fiscal_19022000_1704802_v1_001.json", 
                     repositorio=repositorio,
                     encoding=encoding)
    

    



