from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from SimpleFacturaSDK.models.GetFactura.Documento import Documento
from SimpleFacturaSDK.models.GetFactura.Exportaciones import Exportaciones


@dataclass
class RequestDTE:
    Documento: Optional[Documento] = None
    Exportaciones: Optional[Exportaciones] = None 
    Observaciones: Optional[str] = None
    TipoPago: Optional[str] = None
    Cajero: Optional[str] = None
