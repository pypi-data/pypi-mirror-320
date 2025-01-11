import json
from pathlib import Path
from typing import Type, TypeVar, List, Optional, Dict
from mapafiscal.interfaces.repositorio_interface import RepositorioInterface
from mapafiscal.domain.entities import Aliquota, PautaFiscal, CenarioIncidencia, ExcecaoFiscal


T = TypeVar('T')


class JSONRepositorio(RepositorioInterface[T]):

    DEFAULT_CLAZZ_MAP = {
        Aliquota: "aliquotas.json",
        PautaFiscal: "pautas_fiscais.json",
        CenarioIncidencia: "cenarios_incidencias.json",
        ExcecaoFiscal: "excecoes_fiscais.json",
    }

    def __init__(self, db_path: str, clazz_map: Dict[Type[T], str] = DEFAULT_CLAZZ_MAP, encoding: str = 'utf-8'):
        self.clazz_map = clazz_map
        self.encoding = encoding
        self.arquivos = {clazz.__name__: Path(f"{db_path}/{arquivo}") for clazz, arquivo in self.clazz_map.items()}
        self.dados = {clazz.__name__: self._carregar_dados(clazz) for clazz in self.clazz_map.keys()}

    def _carregar_dados(self, clazz: Type[T]) -> List[T]:
        arquivo = self.arquivos[clazz.__name__]
        if not arquivo.exists():
            return []
        with open(arquivo, 'r', encoding=self.encoding) as f:
            try:
                dados = json.load(f)
                return [clazz(**item) for item in dados]
            except json.JSONDecodeError:
                print(f"Erro ao carregar o arquivo JSON: {arquivo}")
                return []

    def _salvar_dados(self, clazz: Type[T]) -> None:
        arquivo = self.arquivos[clazz.__name__]
        with open(arquivo, 'w', encoding=self.encoding) as f:
            json.dump(self.dados[clazz.__name__], f, default=lambda o: o.__dict__, indent=4)
            
    def _gerar_proximo_id(self, clazz: Type[T]) -> int:
        """
        Gera o próximo ID sequencial para a entidade especificada.

        Args:
            clazz (Type[T]): A classe da entidade.

        Returns:
            int: O próximo ID único.
        """
        if clazz.__name__ in self.dados:
            max_id = max((item.id for item in self.dados[clazz.__name__]), default=0)
            return max_id + 1
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def adicionar(self, obj: T, clazz: Type[T]) -> None:
        if clazz.__name__ in self.dados:
            if not hasattr(obj, 'id') or obj.id is None:  # Gera ID se não estiver definido
                obj.id = self._gerar_proximo_id(clazz)
            self.dados[clazz.__name__].append(obj)
            self._salvar_dados(clazz)
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def obter_por_id(self, id: int, clazz: Type[T]) -> Optional[T]:
        if clazz.__name__ in self.dados:
            return next((item for item in self.dados[clazz.__name__] if item.id == id), None)
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def atualizar(self, obj: T, clazz: Type[T]) -> None:
        if clazz.__name__ in self.dados:            
            for i, item in enumerate(self.dados[clazz.__name__]):
                if item.id == obj.id:
                    self.dados[clazz.__name__][i] = obj
                    break
            self._salvar_dados(clazz)
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def remover(self, id: int, clazz: Type[T]) -> None:
        if clazz.__name__ in self.dados:
            self.dados[clazz.__name__] = [item for item in self.dados[clazz.__name__] if item.id != id]
            self._salvar_dados(clazz)
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def listar_todos(self, clazz: Type[T]) -> List[T]:
        if clazz.__name__ in self.dados:           
            return self.dados[clazz.__name__]
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

