from dataclasses import dataclass

@dataclass
class Aliquota:        
    tributo: str    
    uf: str
    aliquota: float    
    fcp: float = 0.0
    ncm: str = ''
    descricao: str = ''
    ex: str = ''
    id: int = None

    def __str__(self):
        return f"Tributo: {self.tributo}, Aliquota: {self.aliquota}"
 