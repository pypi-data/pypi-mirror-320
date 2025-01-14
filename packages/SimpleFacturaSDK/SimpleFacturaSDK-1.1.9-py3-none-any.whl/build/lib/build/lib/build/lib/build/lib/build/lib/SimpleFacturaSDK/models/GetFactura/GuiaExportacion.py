from dataclasses import dataclass, field
from datetime import datetime
from enumeracion.CodigoTraslado import CodigoTrasladoEnum

@dataclass
class GuiaExportacion:
    CdgTraslado:CodigoTrasladoEnum
    FolioAut: int 
    FechaAutorizacionString: str
    FchAut: datetime 

   