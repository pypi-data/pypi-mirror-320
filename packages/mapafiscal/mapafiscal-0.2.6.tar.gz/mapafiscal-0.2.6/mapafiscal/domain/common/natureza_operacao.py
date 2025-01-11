from enum import Enum, unique
from dataclasses import dataclass

    
@unique    
class NaturezaOperacao(Enum):
    VENDA_PRODUCAO = ("venda_producao", "venda", "saida", "Venda de produção")
    VENDA_MERCADORIA = ("venda_mercadoria", "venda", "saida", "Venda de mercadoria")
    REMESSA_INDUSTRIALIZACAO_SAIDA = ("remessa_industrializacao_saida", "remessa", "saida", "Remessa para industrialização")
    REMESSA_POR_CONTA_ORDEM_SAIDA = ("remessa_por_conta_ordem_saida", "remessa", "saida", "Remsessa por conta de ordem")
    EXPORTACAO = ("exportacao", "venda", "saida", "Exportação")
    TRANSFERENCIA_PRODUCAO_SAIDA = ("transferencia_producao_saida", "transferencia", "saida", "Transferência de produção")
    TRANSFERENCIA_MERCADORIA_SAIDA = ("transferencia_mercadoria_saida", "transferencia", "saida", "Transferência de mercadoria")
    OUTRAS_SAIDAS = ("outras_saidas", "outras", "saidas", "Outras saidas")
    COMPRA_INDUSTRIALIZACAO = ("compra_industrializacao", "compra", "entrada", "Compra para industrialização")
    COMPRA_MERCADORIA = ("compra_mercadoria", "compra", "entrada", "Compra de mercadoria")
    IMPORTACAO = ("importacao", "compra", "entrada", "Importação")
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}")

    @staticmethod
    def list(index = 0):
        return [elem.value[index] for elem in NaturezaOperacao]

    @property
    def tipo_operacao(self):
        return self.value[2]
    
    @property
    def descricao(self):
        return self.value[3]
    
    @property
    def grupo(self):        
        return self.value[1]
    
    @property
    def codigo(self):        
        return self.value[0]
       
    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0] 
      
    def __eq__(self, other):
        if isinstance(other, NaturezaOperacao):
            return self.value[0] == other.value[0]
        if isinstance(other, str):
            return self.value[0] == other
        return False
