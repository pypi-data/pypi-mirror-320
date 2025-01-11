from typing import List
from mapafiscal.domain.aggregates import MapaFiscal, CenarioFiscal, ClasseFiscal, OperacaoFiscal, ClasseST
from mapafiscal.domain.services import MapaFiscalProcessor
from mapafiscal.domain.services.contexto_fiscal import ContextoFiscal
from mapafiscal.domain.common import NaturezaOperacao, Finalidade, TipoCliente, UF
 
class MapaFiscalBuilder:
    '''
    MapaFiscalBuilder - Classe responsável pela construção do Mapa Fiscal a partir de um Contexto Tributário    
    '''    
    def __init__(self, cliente: str, contexto: ContextoFiscal):
        self._mapa_processor = MapaFiscalProcessor(contexto)
        self._contexto = contexto
        self._mapa_fiscal = MapaFiscal(cliente, contexto.uf_origem, contexto.regime_tributacao)
        
    def build(self, nome: str):
        self._mapa_fiscal.nome = nome
        return self._mapa_fiscal
     
    def build_classe_fiscal(self, 
                      codigo: str,
                      ncm: str, 
                      descricao: str,
                      origem: int,
                      cest: str = '', 
                      segmento: str = '',
                      fabricante_equiparado: bool = False) -> ClasseFiscal:
        
        produto = self._mapa_processor.process_classe_fiscal(codigo, ncm, descricao, origem, cest, segmento, fabricante_equiparado)        
        self._mapa_fiscal.classes_fiscais.append(produto)        
        return produto
         
    def build_classes_st(self, classe_fiscal: ClasseFiscal) -> dict[ClasseST]:    
        
        pautas_fiscais = self._contexto.list_pauta_by_cest(cest=classe_fiscal.cest)
        classes_st = {}
        for pauta_fiscal in pautas_fiscais:
            classes_st[pauta_fiscal.uf_destino] = self._mapa_processor.process_classe_st(classe_fiscal, pauta_fiscal)
            self._mapa_fiscal.classes_st.append(classes_st[pauta_fiscal.uf_destino])            
        return classes_st       
       
        
    def build_cenarios(self, 
                      grupo: str, 
                      natureza_operacao: NaturezaOperacao,                        
                      tipo_cliente: TipoCliente, 
                      finalidade: Finalidade,
                      classe_fiscal: ClasseFiscal,
                      uf_list: List[str] = ["__all__"]):

        uf_list = UF.list() if uf_list == ["__all__"] else uf_list
        
        for uf in uf_list:
            self.build_cenario(grupo, natureza_operacao, tipo_cliente, finalidade, classe_fiscal, uf)             
   
    def build_cenario(self, 
                      grupo: str, 
                      natureza_operacao: NaturezaOperacao,                        
                      tipo_cliente: TipoCliente, 
                      finalidade: Finalidade,
                      classe_fiscal: ClasseFiscal,
                      uf: str) -> CenarioFiscal:
    
        if classe_fiscal.icms is None:
            raise MapaFiscalBuilderException(f"Classe Fiscal {classe_fiscal.codigo} sem informações de ICMS")
        
        cenario = self._mapa_processor.process_cenario_fiscal(grupo, 
                                                               natureza_operacao=natureza_operacao, 
                                                               tipo_cliente=tipo_cliente, 
                                                               finalidade=finalidade,
                                                               classe_fiscal=classe_fiscal, 
                                                               uf=uf)
        self._mapa_fiscal.cenarios.append(cenario)              
        return cenario     
     
    def build_operacoes(self, grupo: str, classe_fiscal: ClasseFiscal):        
        for cenario in self._mapa_fiscal.get_cenarios(grupo, classe_fiscal=classe_fiscal):
            self.build_operacao(cenario) 
     
    def build_operacao(self, cenario: CenarioFiscal) -> OperacaoFiscal:
        operacao_fiscal = self._mapa_processor.process_operacao_fiscal(cenario)           
        self._mapa_fiscal.operacoes.append(operacao_fiscal)         
        return operacao_fiscal

class MapaFiscalBuilderException(Exception):
    '''
    MapaFiscalBuilderException para tratamento de exceções do MapaFiscalBuilder.
    '''
    pass