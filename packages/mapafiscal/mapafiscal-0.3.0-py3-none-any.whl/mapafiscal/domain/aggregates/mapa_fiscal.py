from dataclasses import dataclass
from mapafiscal.domain.common import RegimeTributacao, NaturezaOperacao, Finalidade, TipoCliente
from mapafiscal.domain.common import CST_ICMS, CST_IPI, CST_PIS_COFINS
from mapafiscal.domain.entities import ICMS, IPI, PIS_COFINS
from typing import List, Optional


@dataclass           
class MapaFiscal:
    '''
    Mapa Fiscal Tributário - Mapa contendo cenarios e operacoes fiscais para um determinado conjunto de classes fiscais
    '''
    def __init__(self, nome: str, uf_origem: str, tributacao: RegimeTributacao):
        self._nome: str = nome
        self._uf_origem: str = uf_origem
        self._regime_tributacao: RegimeTributacao = tributacao
        self._classes_fiscais: List[ClasseFiscal] = [] 
        self._classes_st: List[ClasseST] = []
        self._operacoes: List[OperacaoFiscal] = []
        self._cenarios: List[CenarioFiscal] = []
    
    @property
    def nome(self):        
        return self._nome
    
    @nome.setter
    def nome(self, value):        
        self._nome = value   
  
    @property
    def uf_origem(self):        
        return self._uf_origem
        
    @property
    def regime_tributario(self):        
        return self._regime_tributacao
    
    @property
    def cenarios(self):        
        return self._cenarios
        
    @property
    def operacoes(self):        
        return self._operacoes   
     
    @property
    def classes_st(self):           
        return self._classes_st
        
    @property
    def classes_fiscais(self):        
        return self._classes_fiscais
        
    def get_classe_fiscal(self, codigo: str) -> 'ClasseFiscal':
        for classe in self._classes_fiscais:
            if classe.codigo == codigo:
                return classe
        return None
    
    def get_cenarios(self, grupo: str, classe_fiscal: 'ClasseFiscal'):
        return [cenario for cenario in self._cenarios if cenario is not None and cenario.grupo == grupo and cenario.classe_fiscal == classe_fiscal]
    
    def get_operacoes(self, grupo: str):
        return [operacao for operacao in self._operacoes if operacao is not None and operacao.cenario == grupo]
    
    def get_classe_st(self, cest: str, uf_destino: str) -> 'ClasseST':
        for classe in self._classes_st:
            if classe.cest == cest and classe.uf_destino == uf_destino:
                return classe
        return None
        
    def __str__(self):        
        return f"Mapa Fiscal: {self._nome}, " \
               f"UF Origem: {self._uf_origem}, " \
               f"Regime Tributação: {self._regime_tributacao}"
    

   
@dataclass
class ClasseFiscal:
    codigo: str
    ncm: str
    origem: int 
    descricao: str 
    cest: str
    segmento: str 
    ipi: Optional[IPI] = None    
    icms: Optional[ICMS] = None
    pis: Optional[PIS_COFINS] = None      
    cofins: Optional[PIS_COFINS] = None 
    fabricante_equiparado: bool = False
     
    def __str__(self):
        return f"Código: {self.codigo}, " \
               f"NCM: {self.ncm}, " \
               f"Origem: {self.origem}, " \
               f"Descricao: {self.descricao}, " \
               f"CEST: {self.cest}"


@dataclass    
class ClasseST:
    cest: str  
    descricao_cest: str
    segmento: str
    uf_origem: str
    uf_destino: str    
    mva_original: float
    mva_ajustada: float
    aliq_icms_operacao: float
    aliq_icms_uf_destino: float
    reducao_bc_icms_st: float
    aliq_fcp_uf_destino: float
    fundamento_legal: str
    
    def __str__(self):
        return f"CEST: {self.cest}, " \
               f"Descricao: {self.descricao_cest}, " \
               f"Segmento: {self.segmento}, " \
               f"Origem: {self.uf_origem}, " \
               f"Destino: {self.uf_destino}"

@dataclass
class CenarioFiscal:
    grupo: str
    classe_fiscal: ClasseFiscal
    uf_origem: str
    uf_destino: str
    natureza_operacao: NaturezaOperacao    
    cfop_interno: str
    cfop_interno_devolucao: str
    cfop_interestadual: str
    cfop_interestadual_devolucao: str
    finalidade: Finalidade
    tipo_cliente: TipoCliente     
    incide_icms: bool
    incide_icms_st: bool
    incide_difal: bool
    cst_icms: CST_ICMS
    incide_ipi: bool
    cst_ipi: CST_IPI    
    incide_pis_cofins: bool
    cst_pis_cofins: CST_PIS_COFINS
    fundamento_legal: str
    codigo_cenario: str  
        
    def __str__(self):
        return f"Grupo: {self.grupo}, " \
               f"NCM: {self.classe_fiscal.ncm}, " \
               f"Natureza Operacao: {self.natureza_operacao}, " \
               f"UF Origem: {self.uf_origem}, " \
               f"UF Destino: {self.uf_destino}"
    

        
@dataclass
class OperacaoFiscal:
    cenario: str    
    uf_origem: str
    uf_destino: str
    natureza_operacao: NaturezaOperacao
    classe_fiscal: ClasseFiscal
    tipo_cliente: TipoCliente
    finalidade: Finalidade  
    cst_icms: CST_ICMS
    cfop_saida: str
    cfop_entrada: str
    aliq_icms_operacao: float
    reducao_bc_icms: float
    aliq_fcp_uf_destino: float
    aliq_icms_uf_destino: float
    reducao_bc_icms_st: float
    ncm: str
    cest: str
    mva_st: float
    difal_icms: float
    difal_icms_st: float
    cst_ipi: CST_IPI
    aliq_ipi: float
    cst_pis: CST_PIS_COFINS
    aliq_pis: float
    cst_cofins: CST_PIS_COFINS
    aliq_cofins: float
    fundamento_legal: str 

    def __str__(self):        
        return f"Operação: {self.cenario}, " \
               f"Natureza Operacao: {self.natureza_operacao}, " \
               f"Tipo Cliente: {self.tipo_cliente}, " \
               f"Finalidade: {self.finalidade}" \
               f"CFOP: {self.cfop_saida}, " \
               f"NCM: {self.classe_fiscal.ncm}, " \
               f"UF Origem: {self.uf_origem}, " \
               f"UF Destino: {self.uf_destino}, " 

 