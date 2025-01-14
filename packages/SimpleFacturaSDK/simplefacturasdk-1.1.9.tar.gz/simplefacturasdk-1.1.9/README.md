# SDK SimpleFactura

El SDK SimpleFactura es una solución en Python diseñada para facilitar la integración con los servicios de SimpleFactura, parte de ChileSystems. Este SDK provee un conjunto de clases y métodos que permiten realizar operaciones como facturación, gestión de productos, proveedores, clientes, sucursales, folios, Datos de empresa y boletas de honorarios.

---

## Características principales

- **Simplifica** la interacción con los servicios de SimpleFactura.
- Proporciona interfaces específicas para operaciones como:
  - **Facturación**: Generación y gestión de documentos tributarios electrónicos.
  - **Gestión** de productos, proveedores y clientes.
  - **Gestión de folios**.
  - **Emisión de boletas de honorarios**.
- Compatible con **Python 3.6 y superior**.

---

## Requisitos

### Dependencias

Las dependencias necesarias para utilizar este SDK son:

- `requests`
- `aiohttp`
- `requests-toolbelt`
- `pydantic`
- `httpx`
- `pytest`
- `requests-mock`
- `python-dotenv`
- `pytest-asyncio`
- `aiofiles`

### Plataforma

El SDK es compatible con **Python 3.6** y versiones superiores.

---

## Instalación

Puedes instalar el SDK y sus dependencias utilizando **pip**:
```bash
pip install SimpleFacturaSDK
```

Si necesitas instalar las dependencias manualmente:
    
```bash
pip install requests requests-toolbelt pydantic aiohttp pytest requests-mock python-dotenv pytest-asyncio httpx aiofiles

```

Opcional(Clonar el repositorio e instalar dependencias desde requirements.txt)
```bash
git clone https://github.com/pereacarlos/SimpleFacturaSDK-python.git
cd SimpleFacturaSDK-python
pip install -r requirements.txt

```

## Configuración del archivo **.env**:
Para usar el SDK, asegúrate de crear un archivo .env en el directorio raíz de tu proyecto. Este archivo debe contener tus credenciales de acceso a la API de SimpleFactura. Aquí tienes un ejemplo de cómo configurarlo:
```bash
SF_USERNAME=tu_usuario
SF_PASSWORD=tu_contraseña
SF_BASE_URL=https://api.simplefactura.cl
PYTHONPATH=.

```
Para garantizar que el archivo **.env** esté disponible en tiempo de ejecución, sigue estos pasos:

1. Crea un archivo llamado .env en el directorio raíz de tu proyecto.
2. Agrega tus credenciales de acceso a la API en el archivo .env como se muestra en el ejemplo anterior.
3. Asegúrate de que el archivo .env esté incluido en tu archivo .gitignore para evitar subir tus credenciales a un repositorio público.

## Configuración del archivo **config.py**:
Para usar el SDK, asegúrate de crear un archivo **config.py** en el directorio raíz de tu proyecto. Este archivo debe contener tus la url de acceso a la API de SimpleFactura. Aquí tienes un ejemplo de cómo configurarlo:
```bash
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("SF_BASE_URL")
```

Cómo empezar
Para utilizar el SDK, simplemente inicializa la clase ClientSimpleFactura proporcionando tu nombre de usuario y contraseña:
```bash
from ClientSimpleFactura import ClientSimpleFactura
import os
from dotenv import load_dotenv
load_dotenv()

username = os.getenv("SF_USERNAME")
password = os.getenv("SF_PASSWORD")

def main():
    client_api = ClientSimpleFactura(username, password)
    
    # Ejemplo: Uso de los servicios
    facturacionService = client_api.Facturacion
    productoService = client_api.Productos
    proveedorService = client_api.Proveedores
    clientesService = client_api.Clientes
    sucursalService = client_api.Sucursales
    folioService = client_api.Folios
    configuracionService = client_api.ConfiguracionService
    boletaHonorarioService = client_api.BoletaHonorarioService

if __name__ == "__main__":
    main()

```

### Ejemplo de Uso del SDK SimpleFactura y Descripción General del Código

#### ObtenerPDF
Este ejemplo demuestra cómo utilizar el SDK `SimpleFacturaSdk` para interactuar con el servicio de facturación electrónica SimpleFactura. Específicamente, se realiza una solicitud para descargar el PDF de una factura electrónica. El proceso incluye:

1. **Configuración de Credenciales**: Las credenciales se obtienen de un archivo `.env` para autenticar al usuario.
2. **Creación de Solicitud**: Se configura una solicitud con los datos necesarios, como el RUT del emisor, tipo de documento, y folio.
3. **Llamada al Servicio**: Se utiliza el cliente del SDK para llamar al endpoint `/dte/pdf` y obtener el PDF de la factura.
4. **Guardado del PDF**: Si la respuesta es exitosa, el archivo PDF se guarda localmente.

El código utiliza programación asincrónica para garantizar un manejo eficiente de la comunicación con la API.

```bash
import asyncio
from SimpleFacturaSDK.client_simple_factura import ClientSimpleFactura
from SimpleFacturaSDK.models.GetFactura.Credenciales import Credenciales
from SimpleFacturaSDK.models.GetFactura.DteReferenciadoExterno import DteReferenciadoExterno
from SimpleFacturaSDK.models.GetFactura.SolicitudPdfDte import SolicitudPdfDte
import os
from dotenv import load_dotenv
load_dotenv()

username = os.getenv("SF_USERNAME")
password = os.getenv("SF_PASSWORD")

async def main():

    async with ClientSimpleFactura(username, password) as client_api:
        pdf = SolicitudPdfDte(
            credenciales=Credenciales(
                rut_emisor="76269769-6",
                nombre_sucursal="Casa Matriz"
            ),
            dte_referenciado_externo=DteReferenciadoExterno(
                folio=4117,
                codigoTipoDte=33,
                ambiente=0
            )
        )
        try:
            pdf_response = await client_api.Facturacion.obtener_pdf(pdf)
            if pdf_response.status == 200:
                with open("factura.pdf", "wb") as file:
                    file.write(pdf_response.data)
                print("PDF guardado exitosamente")
            else:
                print(f"Error: {pdf_response.message}")
        except Exception as err:
            print(f"Error: {err}")

if __name__ == "__main__":
    asyncio.run(main())
```
#### ObtenerTimbre

Este ejemplo utiliza el SDK `SimpleFacturaSdk` para obtener el timbre de una factura electrónica desde el servicio SimpleFactura. El proceso incluye:

1. **Configuración de Credenciales**: Las credenciales se obtienen de un archivo `.env` para autenticar al usuario.
2. **Creación de Solicitud**: Se configura una solicitud que incluye datos como el RUT del emisor, nombre de la sucursal, folio, tipo de documento, y ambiente.
3. **Llamada al Servicio**: Se realiza una llamada al endpoint correspondiente para obtener el timbre asociado a la factura.
4. **Guardado del Timbre**: Si la respuesta es exitosa, el timbre recibido en formato Base64 se decodifica y se guarda como una imagen en el archivo `timbre.png`.
El código utiliza programación asincrónica para manejar las solicitudes y asegura un manejo eficiente de los recursos y errores durante la ejecución.

```bash
import asyncio
from SimpleFacturaSDK.client_simple_factura import ClientSimpleFactura
from SimpleFacturaSDK.models.GetFactura.Credenciales import Credenciales
from SimpleFacturaSDK.models.GetFactura.DteReferenciadoExterno import DteReferenciadoExterno
from SimpleFacturaSDK.models.GetFactura.SolicitudPdfDte import SolicitudPdfDte
import base64
import json
import os
from dotenv import load_dotenv
load_dotenv()
username = os.getenv("SF_USERNAME")
password = os.getenv("SF_PASSWORD")
async def main():
    async with ClientSimpleFactura(username, password) as client_api:
        solicitud = SolicitudPdfDte(
            credenciales=Credenciales(
                rut_emisor="76269769-6",
                nombre_sucursal="Casa Matriz"
            ),
            dte_referenciado_externo=DteReferenciadoExterno(
                folio=4117,
                codigoTipoDte=33,
                ambiente=0
            )
        )
        try:
            timbre_response = await client_api.Facturacion.obtener_timbre(solicitud)
            timbre_data = json.loads(timbre_response.data)
            with open("timbre.png", "wb") as f:
                f.write(base64.b64decode(timbre_data["data"]))
            print("Timbre guardado en timbre.png")
        except Exception as err:
            print(f"Error: {err}")
if __name__ == "__main__":
    asyncio.run(main())

```


##### Facturacion_individualV2_Boletas
Este ejemplo muestra cómo utilizar el SDK `SimpleFacturaSdk` para emitir una boleta electrónica mediante el servicio SimpleFactura. El proceso incluye:

1. **Configuración de Credenciales**: Las credenciales se obtienen de un archivo `.env` para autenticar al usuario.
2. **Creación de Solicitud**: Se configura una solicitud detallada con información del documento, encabezado, emisor, receptor, totales, y los productos o servicios incluidos.
3. **Llamada al Servicio**: Se utiliza el cliente del SDK para llamar al endpoint de facturación de boletas, enviando los datos configurados.
4. **Respuesta del Servicio**: Se procesa la respuesta del servicio, mostrando detalles como el tipo de documento, RUT del emisor y receptor, folio, fecha de emisión y el total del documento.

El código utiliza programación asincrónica para manejar eficientemente las solicitudes hacia la API y captura errores para un manejo robusto en caso de fallos.
```bash
import asyncio
from SimpleFacturaSDK.client_simple_factura import ClientSimpleFactura
import base64
import json
from SimpleFacturaSDK.models.GetFactura.Documento import Documento
from SimpleFacturaSDK.models.GetFactura.Encabezado import Encabezado
from SimpleFacturaSDK.models.GetFactura.IdentificacionDTE import IdDoc
from SimpleFacturaSDK.models.GetFactura.Emisor import Emisor
from SimpleFacturaSDK.models.GetFactura.Receptor import Receptor
from SimpleFacturaSDK.models.GetFactura.Totales import Totales
from SimpleFacturaSDK.models.GetFactura.Detalle import Detalle
from SimpleFacturaSDK.models.GetFactura.CodigoItem import CdgItem
from SimpleFacturaSDK.enumeracion.TipoDTE import DTEType
from SimpleFacturaSDK.enumeracion.IndicadorServicio import IndicadorServicioEnum
from SimpleFacturaSDK.models.GetFactura.RequestDTE import RequestDTE
import requests
from models.ResponseDTE import Response
import os
from dotenv import load_dotenv
load_dotenv()

username = os.getenv("SF_USERNAME")
password = os.getenv("SF_PASSWORD") 
async def main():
   async with ClientSimpleFactura(username, password) as client_api:
        solicitud = RequestDTE(
            Documento=Documento(
                Encabezado=Encabezado(
                    IdDoc=IdDoc(
                        TipoDTE=DTEType.BoletaElectronica,
                        FchEmis="2024-09-03",
                        FchVenc="2024-09-03",
                        IndServicio=IndicadorServicioEnum.BoletaVentasYServicios,
                    ),
                    Emisor=Emisor(
                        RUTEmisor="76269769-6",
                        RznSocEmisor="Chilesystems",
                        GiroEmisor="Desarrollo de software",
                        DirOrigen="Calle 7 numero 3",
                        CmnaOrigen="Santiago"
                    ),
                    Receptor=Receptor(
                        RUTRecep="17096073-4",
                        RznSocRecep="Proveedor Test",
                        DirRecep="calle 12",
                        CmnaRecep="Paine",
                        CiudadRecep="Santiago",
                        CorreoRecep="mercocha13@gmail.com",
                    ),
                    Totales=Totales(
                        MntNeto="8320",
                        IVA="1580",
                        MntTotal="9900"
                    )
                ),
                Detalle=[
                    Detalle(
                        NroLinDet="1",
                        DscItem="Desc1",
                        NmbItem="Producto Test",
                        QtyItem="1",
                        UnmdItem="un",
                        PrcItem="100",
                        MontoItem="100",
                        CdgItem=[]
                    ),
                    Detalle(
                        NroLinDet="2",
                        CdgItem=[
                            CdgItem(
                                TpoCodigo="ALFA",
                                VlrCodigo="123"
                            )
                        ],
                        DscItem="Desc2",
                        NmbItem="Producto Test",
                        QtyItem="1",
                        UnmdItem="un",
                        PrcItem="100",
                        MontoItem="100"
                        
                    )
                ]
            ),
            Observaciones="NOTA AL PIE DE PAGINA",
            Cajero="CAJERO",
            TipoPago="CONTADO"
        )
        try:
            Boleta = await client_api.Facturacion.facturacion_individualV2_Boletas(solicitud, "Casa Matriz")
            print("\nDatos de la Respuesta:")
            print(f"Status: {Boleta.status}")
            print(f"Message: {Boleta.message}")
            print(f"TipoDTE: {Boleta.data.tipoDTE}")
            print(f"RUT Emisor: {Boleta.data.rutEmisor}")
            print(f"RUT Receptor: {Boleta.data.rutReceptor}")
            print(f"Folio: {Boleta.data.folio}")
            print(f"Fecha Emision: {Boleta.data.fechaEmision}")
            print(f"Total: {Boleta.data.total}")
            print(Boleta.data)
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            print("Detalle del error:", http_err.response.text)
        except Exception as err:
            print(f"Error: {err}")
  
if __name__ == "__main__":
    asyncio.run(main())

```

## Documentación
La documentación relevante para usar este SDK es:

- Documentación general:
  [Sitio Simple Factura](https://www.simplefactura.cl/).
- Documentacion de APIs [Postman](https://documentacion.simplefactura.cl/).
