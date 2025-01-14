from SimpleFacturaSDK.client_simple_factura import ClientSimpleFactura
from SimpleFacturaSDK.models.ResponseDTE import Response
from SimpleFacturaSDK.models.GetFactura.Credenciales import Credenciales
import base64
import requests
import json
import unittest
from dotenv import load_dotenv
import aiohttp
from unittest.mock import AsyncMock, patch
import os
load_dotenv()

class TestConfiguracionService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        username = os.getenv("SF_USERNAME")
        password = os.getenv("SF_PASSWORD")
        self.client_api = await ClientSimpleFactura(username, password).__aenter__()
        self.service = self.client_api.ConfiguracionService

    async def test_DatosEmpresa_ReturnOK(self):
        solicitud= Credenciales(
            rut_emisor="76269769-6"
        )
        response = await self.service.datos_empresa(solicitud)
        self.assertEqual(response.status, 200)
        self.assertIsNotNone(response.data)
        self.assertIsNotNone(response.data.rut)
        self.assertIsNotNone(response.data.razonSocial)
        self.assertIsNotNone(response.data.giro)

    async def test_DatosEmpresa_ReturnServerError_whenDatosIsInvalid(self):
        solicitud= Credenciales(
            rut_emisor=""
        )
        response = await self.service.datos_empresa(solicitud)
        self.assertEqual(response.status, 500)
        self.assertIsNone(response.data)
        self.assertIsNotNone(response.message)

    async def test_DatosEmpresa_ReturnServerError_WhenMethodPostIsInvalid(self):
        solicitud= Credenciales(
            rut_emisor=""
        )
        with patch('aiohttp.ClientSession.post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Error al ObtenerDatos de la Empresa")

            response = await self.service.datos_empresa(solicitud)
            self.assertEqual(response.status, 500)
            self.assertIsNone(response.data)
            self.assertIsNotNone(response.message)







