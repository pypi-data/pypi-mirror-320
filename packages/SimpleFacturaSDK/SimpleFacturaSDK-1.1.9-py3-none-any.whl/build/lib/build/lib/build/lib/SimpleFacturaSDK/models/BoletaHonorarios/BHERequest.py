from typing import Optional
from dataclasses import dataclass
from models.GetFactura.Credenciales import Credenciales

@dataclass
class BHERequest:
    credenciales: Credenciales
    Folio: int

