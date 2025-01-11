from mapafiscal.domain.services.contexto_fiscal import ContextoFiscal
from mapafiscal.domain.entities import PautaFiscal, ICMS, IPI, PIS_COFINS
from mapafiscal.domain.common import Finalidade, TipoCliente, NaturezaOperacao, TipoIncidencia, CST_ICMS, CST_IPI, CST_PIS_COFINS
from mapafiscal.domain.aggregates import ClasseFiscal, OperacaoFiscal, CenarioFiscal, ClasseST


class MapaFiscalProcessor():
    
    """
    Motor de regras fiscais para construção de mapa fiscal a partir de um contexto fiscal.
    """

    def __init__(self, contexto: ContextoFiscal):
        """
        Inicializa o processador com os dados do contexto fiscal.

        Args:
            dados (ContextoFiscalData): Fonte de dados para processamento.
        """
        self._contexto = contexto
    
    @property
    def contexto(self):
        return self._contexto
    
    def calculate_icms(self, ncm: str, uf: str) -> ICMS:     
        """
        Calcula a incidência de ICMS para um NCM e UF.

        Args:
            ncm (str): NCM do produto.
            uf (str): Unidade Federativa.

        Returns:
            ICMS: Configuração calculada do ICMS.
        """
        excecao = self._contexto.find_excecao_fiscal(ncm=ncm, uf=uf, tributo="ICMS")
        if excecao:
            return ICMS(
                cst=CST_ICMS.from_value(excecao.cst),
                aliquota=excecao.aliquota,
                reducao_base_calculo=excecao.reducao_base_calculo,
                fcp=excecao.fcp,
                fundamento_legal=excecao.fundamento_legal
            )
        else:
            aliquota = self._contexto.find_aliquota(tributo="ICMS", uf=uf, ncm=ncm)
            return ICMS(
                cst=CST_ICMS.CST_00,
                aliquota=aliquota.aliquota,
                reducao_base_calculo=0.0,
                fcp=aliquota.fcp,
                fundamento_legal=""
            )  

    def calculate_aliquota_icms(self, ncm: str, origem: int, uf_destino: str) -> float:
        """
        Obtém a aliquota para uma operação de ICMS.
        
        A aliquota depende do NCM, origem e UF de destino e origem.
        """
        if uf_destino == self._contexto.uf_origem:
            return self.calculate_icms(ncm=ncm, uf=uf_destino).aliquota            
        if origem in [0, 4, 5, 6, 7]:
            if uf_destino in ['SP', 'MG', 'RJ', 'SC', 'PR', 'RS']:
                return 12.0
            else:
                return 7.0                
        else:
            return 4.00    

    def calculate_pis(self, ncm: str) -> PIS_COFINS:
        """
        Calcula a incidência de PIS para um NCM.

        Args:
            ncm (str): NCM do produto.

        Returns:
            PIS_COFINS: Configuração calculada do PIS.
        """
        excecao = self._contexto.find_excecao_fiscal(ncm=ncm, tributo="PIS")
        if excecao:
            return PIS_COFINS(
                cst=CST_PIS_COFINS.from_value(excecao.cst),
                aliquota=excecao.aliquota,
                fundamento_legal=excecao.fundamento_legal
            )
        else:
            aliquota = self._contexto.find_aliquota(tributo="PIS", ncm=ncm)
            return PIS_COFINS(
                cst=CST_PIS_COFINS.CST_01,
                aliquota=aliquota.aliquota,
                fundamento_legal=""
            )
    
    def calculate_cofins(self, ncm: str) -> PIS_COFINS:
        """
        Calcula a incidência da COFINS para um NCM.

        Args:
            ncm (str): NCM do produto.

        Returns:
            PIS_COFINS: Configuração calculada do COFINS.
        """
        excecao = self._contexto.find_excecao_fiscal(ncm=ncm, tributo="COFINS")
        if excecao:
            return PIS_COFINS(
                cst=CST_PIS_COFINS.from_value(excecao.cst),
                aliquota=excecao.aliquota,
                fundamento_legal=excecao.fundamento_legal
            )
        else:
            aliquota = self._contexto.find_aliquota(tributo="COFINS", ncm=ncm)
            return PIS_COFINS(
                cst=CST_PIS_COFINS.CST_01,
                aliquota=aliquota.aliquota,
                fundamento_legal=""
            )
    
    def calculate_ipi(self, ncm: str, fabricante: bool = True) -> IPI: 
        """
        Calcula a incidência do IPI para um NCM.

        Args:
            ncm (str): NCM do produto.

        Returns:
            IPI: Configuração calculada do IPI.
        """       
        excecao = self._contexto.find_excecao_fiscal(ncm=ncm, tributo="IPI")
        if excecao:
            return IPI(
                cst=CST_IPI.from_value(excecao.cst),
                descricao_tipi=excecao.descricao,
                aliquota=excecao.aliquota,
                fundamento_legal=excecao.fundamento_legal
            )    
        else:
            aliquota = self._contexto.find_aliquota(tributo="IPI", ncm=ncm)
            return IPI(
                cst=CST_IPI.CST_51 if aliquota.aliquota == 0.0 else CST_IPI.CST_50, 
                aliquota=aliquota.aliquota, 
                descricao_tipi=aliquota.descricao,
                fundamento_legal=""
            )
    
    
    def process_classe_fiscal(self, 
                              codigo: str,
                              ncm: str, 
                              descricao: str,
                              origem: int,
                              cest: str = '', 
                              segmento: str = '',
                              fabricante: bool = False) -> ClasseFiscal:

        return ClasseFiscal(
            codigo=codigo,
            ncm=ncm,
            origem=origem,
            descricao=descricao,
            cest=cest,
            segmento=segmento,
            icms=self.calculate_icms(ncm=ncm, uf=self._contexto.uf_origem),
            pis=self.calculate_pis(ncm),
            cofins=self.calculate_cofins(ncm),
            ipi=self.calculate_ipi(ncm=ncm, fabricante=fabricante),
            fabricante_equiparado=fabricante
        )
    
    def process_classe_st(self, classe_fiscal: ClasseFiscal, pauta_fiscal: PautaFiscal) -> ClasseST:
        
        uf_destino = pauta_fiscal.uf_destino
        mva_original = pauta_fiscal.mva_original        
        mva_ajustada = 0.0
        
        icms_operacao = self.calculate_aliquota_icms(
            ncm=classe_fiscal.ncm, 
            origem=classe_fiscal.origem, 
            uf_destino=uf_destino
            )
        
        icms_destino = self.calculate_icms(ncm=classe_fiscal.ncm, uf=uf_destino)        
    
        if self._contexto.uf_origem == uf_destino: # Operação interna   
            mva_ajustada = mva_original 
        else: # Operação interestadual            
            mva_ajustada = round((((1 + mva_original / 100.0) * (1 - icms_operacao / 100.0) / (1 - icms_destino.aliquota / 100.0)) - 1) * 100.0, 4)                
                                    
        return ClasseST(cest=classe_fiscal.cest, 
                      descricao_cest=pauta_fiscal.descricao_cest, 
                      segmento=classe_fiscal.segmento, 
                      uf_origem=self._contexto.uf_origem,
                      uf_destino=uf_destino,                       
                      mva_original=mva_original, 
                      mva_ajustada=mva_ajustada, 
                      aliq_icms_operacao=icms_operacao, 
                      reducao_bc_icms_st=icms_destino.reducao_base_calculo, 
                      aliq_icms_uf_destino=icms_destino.aliquota, 
                      aliq_fcp_uf_destino=icms_destino.fcp, 
                      fundamento_legal=pauta_fiscal.fundamento_legal)
            
                                                             
    def process_cenario_fiscal(self,
                               grupo: str, 
                               natureza_operacao: NaturezaOperacao, 
                               uf: str,                    
                               tipo_cliente: TipoCliente, 
                               finalidade: Finalidade,
                               classe_fiscal: ClasseFiscal) -> CenarioFiscal:
            
        # CST padrão
        cst_icms = CST_ICMS.CST_90
        cst_pis_cofins =  CST_PIS_COFINS.CST_99
        cst_ipi = CST_IPI.CST_99
    
        # Buscar cenario incidencia de acordo com os parâmetros selecionados
        incidencia = self._contexto.find_cenario_incidencia(natureza_operacao=natureza_operacao,
                                                            tipo_cliente=tipo_cliente, 
                                                            finalidade=finalidade) 
        if incidencia == None:
            raise MapaFiscalProcessorException(f'Nao foi possivel identificar um cenario para o NCM {classe_fiscal.ncm}' \
                                            f'na natureza de operacao {natureza_operacao}, ' \
                                            f'tipo de cliente {tipo_cliente} e finalidade {finalidade}')
        
        match (incidencia.incidencia_icms):
            case TipoIncidencia.TRIBUTADO:
                cst_icms = self.calculate_icms(ncm=classe_fiscal.ncm, uf=uf).cst    
            case TipoIncidencia.NAO_TRIBUTADO: 
                cst_icms = CST_ICMS.CST_41
            case TipoIncidencia.ISENTO:
                cst_icms = CST_ICMS.CST_40
            case TipoIncidencia.DIFERIDO:
                cst_icms = CST_ICMS.CST_51
            case TipoIncidencia.SUSPENSO:
                cst_icms = CST_ICMS.CST_50
            case TipoIncidencia.RETIDO:
                cst_icms = CST_ICMS.CST_60
            
        if incidencia.incidencia_icms_st == TipoIncidencia.TRIBUTADO and classe_fiscal.cest != '':        
            # Incide ICMS ST        
            pauta_fiscal = self._contexto.find_pauta_fiscal(cest=classe_fiscal.cest, uf_destino=uf)             
            if pauta_fiscal != None:    
                # Se incidir ICMS ST substituir CST ICMS se necessário        
                match(classe_fiscal.icms.cst):
                    case CST_ICMS.CST_20:
                        cst_icms = CST_ICMS.CST_70
                    case CST_ICMS.CST_40:
                        cst_icms = CST_ICMS.CST_30  
                    case _:
                        cst_icms = CST_ICMS.CST_10
                    
        match(incidencia.incidencia_ipi):
            case TipoIncidencia.TRIBUTADO:
                if classe_fiscal.fabricante_equiparado:
                    cst_ipi = self.calculate_ipi(ncm=classe_fiscal.ncm).cst
            case TipoIncidencia.NAO_TRIBUTADO:
                cst_ipi = CST_IPI.CST_53
            case TipoIncidencia.ISENTO:
                cst_ipi = CST_IPI.CST_52
            case TipoIncidencia.SUSPENSO:
                cst_ipi = CST_IPI.CST_55
        
        match(incidencia.incidencia_pis_cofins):          
            case TipoIncidencia.TRIBUTADO:
                cst_pis_cofins = self.calculate_pis(ncm=classe_fiscal.ncm).cst
            case TipoIncidencia.NAO_TRIBUTADO:
                cst_pis_cofins = CST_PIS_COFINS.CST_08
            case TipoIncidencia.ISENTO:
                cst_pis_cofins = CST_PIS_COFINS.CST_07
            case TipoIncidencia.SUSPENSO:
                cst_pis_cofins = CST_PIS_COFINS.CST_09
     
        incide_icms = cst_icms in [CST_ICMS.CST_00,
                                    CST_ICMS.CST_10,
                                    CST_ICMS.CST_20,
                                    CST_ICMS.CST_70]
        
        incide_icms_st = cst_icms in [CST_ICMS.CST_10,
                                       CST_ICMS.CST_30,
                                       CST_ICMS.CST_60,
                                       CST_ICMS.CST_70]
        
        incide_difal = incide_icms and finalidade in [Finalidade.USO_CONSUMO, Finalidade.IMOBILIZADO] and \
            tipo_cliente in [TipoCliente.CONSTRUCAO_CIVIL, TipoCliente.PRESTADOR_SERVICO, TipoCliente.CONSUMIDOR_FINAL, TipoCliente.PJ_NAO_CONTRIBUINTE]
        
        incide_ipi = cst_ipi in [CST_IPI.CST_50, CST_IPI.CST_51] 
               
        incide_pis_cofins = cst_pis_cofins in [CST_PIS_COFINS.CST_01,
                                               CST_PIS_COFINS.CST_02,
                                               CST_PIS_COFINS.CST_03,
                                               CST_PIS_COFINS.CST_04,
                                               CST_PIS_COFINS.CST_05,
                                               CST_PIS_COFINS.CST_06]
     
        return CenarioFiscal(grupo=grupo, 
                                 classe_fiscal=classe_fiscal, 
                                 uf_origem=self._contexto.uf_origem, 
                                 uf_destino=uf, 
                                 natureza_operacao=natureza_operacao, 
                                 cfop_interno=incidencia.cfop_interno if incide_icms_st==False else incidencia.cfop_interno_st, 
                                 cfop_interno_devolucao=incidencia.cfop_interno_devolucao if incide_icms_st==False else incidencia.cfop_interno_devolucao_st, 
                                 cfop_interestadual=incidencia.cfop_interestadual if incide_icms_st==False else incidencia.cfop_interestadual_st, 
                                 cfop_interestadual_devolucao=incidencia.cfop_interestadual_devolucao if incide_icms_st==False else incidencia.cfop_interestadual_devolucao_st, 
                                 finalidade=finalidade, 
                                 tipo_cliente=tipo_cliente,                                  
                                 incide_icms=incide_icms, 
                                 incide_icms_st=incide_icms_st, 
                                 incide_difal=incide_difal, 
                                 cst_icms=cst_icms,                                  
                                 incide_ipi=incide_ipi, 
                                 cst_ipi=cst_ipi,
                                 incide_pis_cofins=incide_pis_cofins, 
                                 cst_pis_cofins=cst_pis_cofins,                                 
                                 fundamento_legal=incidencia.fundamento_legal,
                                 codigo_cenario=incidencia.codigo)
                
            
    
    def process_operacao_fiscal(self, cenario: CenarioFiscal) -> OperacaoFiscal:        
        
        cfop_saida = ""
        cfop_entrada = ""
        fundamento_legal = ""
        aliq_icms_operacao = 0.0
        aliq_icms_uf_destino = 0.0
        difal_icms = False
        difal_icms_st = False
        
        # Processar a incidência de ICMS-ST
        if cenario.incide_icms_st:   
            pauta_fiscal = self._contexto.find_pauta_fiscal(cest=cenario.classe_fiscal.cest, uf_destino=cenario.uf_destino)         
            icms_st = self.process_classe_st(classe_fiscal=cenario.classe_fiscal, pauta_fiscal=pauta_fiscal)
            
            if icms_st is None:
                raise MapaFiscalProcessorException(f"Classe ST para NCM {cenario.classe_fiscal.ncm} e UF Destino {cenario.uf_destino} desconhecida.")
            fundamento_legal = self.__concat_text(fundamento_legal, icms_st.fundamento_legal)
        
        # Processar a incidência de ICMS (origem e destino)
        if cenario.incide_icms:         
            
            icms_origem = self.calculate_icms(ncm=cenario.classe_fiscal.ncm, uf=cenario.uf_origem)  
            # Operação interna 
            if cenario.uf_destino == cenario.uf_origem:  
                aliq_icms_operacao = icms_origem.aliquota
                cfop_saida = cenario.cfop_interno
                cfop_entrada = cenario.cfop_interno_devolucao
                fundamento_legal = self.__concat_text(fundamento_legal, icms_origem.fundamento_legal) 
            
            # Operação interestadual
            else:                 
                aliq_icms_operacao = self.calculate_aliquota_icms(
                    ncm=cenario.classe_fiscal.ncm, 
                    origem=cenario.classe_fiscal.origem, 
                    uf_destino=cenario.uf_destino) 
                                   
                cfop_saida = cenario.cfop_interestadual
                cfop_entrada = cenario.cfop_interestadual_devolucao
               
        # Processar a incidência de DIFAL 
        if cenario.incide_difal:
            aliq_icms_uf_destino = self.calculate_aliquota_icms(
                ncm=cenario.classe_fiscal.ncm, 
                origem=cenario.classe_fiscal.origem, 
                uf_destino=cenario.uf_destino
            )
            difal_icms = aliq_icms_uf_destino - aliq_icms_operacao if cenario.incide_icms_st == False else 0.0
            difal_icms_st = aliq_icms_uf_destino - aliq_icms_operacao if cenario.incide_icms_st else 0.0
        
        return OperacaoFiscal(
            cenario=cenario.grupo,
            uf_origem=cenario.uf_origem,
            uf_destino=cenario.uf_destino,
            natureza_operacao=cenario.natureza_operacao,
            classe_fiscal=cenario.classe_fiscal,
            tipo_cliente=cenario.tipo_cliente,
            finalidade=cenario.finalidade,
            cst_icms=cenario.cst_icms,
            cfop_saida=cfop_saida,
            cfop_entrada=cfop_entrada,
            aliq_icms_operacao=aliq_icms_operacao,
            reducao_bc_icms=icms_origem.reducao_base_calculo if cenario.incide_icms else 0.0,
            reducao_bc_icms_st=icms_st.reducao_bc_icms_st if cenario.incide_icms_st else 0.0,            
            aliq_fcp_uf_destino=icms_st.aliq_fcp_uf_destino if cenario.incide_icms_st else 0.0,
            aliq_icms_uf_destino=icms_st.aliq_icms_uf_destino if cenario.incide_icms_st else 0.0,
            ncm=cenario.classe_fiscal.ncm,
            cest=cenario.classe_fiscal.cest,
            mva_st=icms_st.mva_ajustada if cenario.incide_icms_st else 0.0,
            difal_icms=difal_icms,
            difal_icms_st=difal_icms_st,
            cst_ipi=cenario.cst_ipi,
            aliq_ipi=cenario.classe_fiscal.ipi.aliquota if cenario.incide_ipi else 0.0,            
            cst_pis=cenario.cst_pis_cofins,
            aliq_pis=cenario.classe_fiscal.pis.aliquota if cenario.incide_pis_cofins else 0.0,
            cst_cofins=cenario.cst_pis_cofins,
            aliq_cofins=cenario.classe_fiscal.cofins.aliquota if cenario.incide_pis_cofins else 0.0,
            fundamento_legal=fundamento_legal
        )

    
    def __concat_text(self, current_text: str, new_text: str) -> str:
        if current_text == '':
            return new_text
        else:
            if new_text != '' and new_text not in current_text:
                return current_text + ', ' + new_text
            else:
                return current_text

            
class MapaFiscalProcessorException(Exception):
    pass