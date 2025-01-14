import os
import json

import httpx

from colppy.helpers.logger import logger
from colppy.models.auth import LoginRequest, LoginResponse, LogoutRequest, LogoutResponse
from colppy.models.clientes import ClientesRequest, ClientesResponse, Cliente
from colppy.models.cobro_factura import CobroFacturaResponse, CobroFacturaRequest, CobroFactura
from colppy.models.compras_pago_details import ComprasPagoDetailsRequest, ComprasPagoDetailsResponse
from colppy.models.comprobante_compra_details import ComprobanteCompraDetailsRequest, ComprobanteCompraDetailsResponse
from colppy.models.comprobante_venta_details import ComprobateVentaDetailsRequest, ComprobanteVentaDetailsResponse
from colppy.models.comprobantes_compra import ComprobanteCompraRequest, ComprobanteCompraResponse
from colppy.models.comprobantes_venta import ComprobanteVentaRequest, ComprobanteVentaResponse
from colppy.models.empresas import EmpresasRequest, Empresa, EmpresasResponse
from colppy.models.movimientos import MovimientosRequest, MovimientosResponse, Movimiento
from colppy.models.proveedores import ProveedoresRequest, ProveedoresResponse, Proveedor

def get_config():
    try:
        config_path = os.path.join(os.getcwd(), 'config.json')
        with open(config_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        raise FileNotFoundError(
            "No se encontró el archivo config.json en el directorio raíz. "
            "Por favor, crea un archivo config.json en el directorio donde estás ejecutando tu aplicación."
        )


class ColppyAPIClient:
    def __init__(self):
        config = get_config()
        self._base_url = config['ColppyAPI']['COLPPY_API_URI']
        self._auth_user = config['ColppyAPI']['COLPPY_AUTH_USER']
        self._auth_password = config['ColppyAPI']['COLPPY_AUTH_PASSWORD']
        self._params_user = config['ColppyAPI']['COLPPY_PARAMS_USER']
        self._params_password = config['ColppyAPI']['COLPPY_PARAMS_PASSWORD']
        self._client = httpx.Client()
        self._token = None

    async def get_token(self) -> str or None:
        login_request = LoginRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            params_password=self._params_password
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=login_request.to_dict())
                response.raise_for_status()
                login_response = LoginResponse(response.json())
                self._token = login_response.get_token()
                logger.debug(f"Token: {self._token}")
                return login_response.get_token()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting token: {e}")
                return None

    async def get_empresas(self, filters=None, start=0, limit=10) -> list[Empresa]:
        empresas_request = EmpresasRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            filters=filters,
            start=start,
            limit=limit,
            token=self._token
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=empresas_request.to_dict())
                response.raise_for_status()
                empresas_response = EmpresasResponse(response.json())
                logger.debug(f"Empresas: {len(empresas_response.get_empresas())}")
                return empresas_response.get_empresas()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting empresas: {e}")
                return []

    async def get_clientes_by_empresa(self, empresa: Empresa, start=0, limit=50) -> list[Cliente]:
        logger.debug(f"Getting clientes for empresa: {empresa.id_empresa}")
        clientes_request = ClientesRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token,
            id_empresa=empresa.id_empresa,
            only_active=True,
            start=start,
            limit=limit
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=clientes_request.to_dict())
                response.raise_for_status()
                clientes_response = ClientesResponse(response.json())
                return clientes_response.get_clientes()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting clientes: {e}")
                return []

    async def get_proveedores_by_empresa(self, empresa: Empresa, start=0, limit=100) -> list[Proveedor]:
        proveedores_request = ProveedoresRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token,
            start=start,
            limit=limit,
            id_empresa=empresa.id_empresa
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=proveedores_request.to_dict())
                response.raise_for_status()
                proveedores_response = ProveedoresResponse(response.json())
                logger.debug(f"Proveedores: {len(proveedores_response.get_proveedores())}")
                return proveedores_response.get_proveedores()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting proveedores: {e}")
                return []

    async def get_comprobantes_compras_by_empresa(self, empresa: Empresa, id_tipo_comprobante=None, filters=None,
                                                  start=0,
                                                  limit=100):
        comprobantes_compra_request = ComprobanteCompraRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token,
            id_empresa=empresa.id_empresa,
            id_tipo_comprobante=id_tipo_comprobante,
            filters=filters,
            start=start,
            limit=limit
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=comprobantes_compra_request.to_dict(), timeout=240)
                response.raise_for_status()
                comprobantes_compra_response = ComprobanteCompraResponse(response.json())
                logger.debug(f"Comprobantes de compra: {len(comprobantes_compra_response.get_comprobantes())}")
                return comprobantes_compra_response.get_comprobantes()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting comprobantes de compra: {e}")
                return []

    async def get_comprobantes_ventas_by_empresa(self, empresa: Empresa, id_tipo_comprobante=None, filters=None,
                                                 start=0,
                                                 limit=100):
        comprobantes_venta_request = ComprobanteVentaRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token,
            id_empresa=empresa.id_empresa,
            id_tipo_comprobante=id_tipo_comprobante,
            filters=filters,
            start=start,
            limit=limit
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=comprobantes_venta_request.to_dict(), timeout=240)
                response.raise_for_status()
                comprobantes_venta_response = ComprobanteVentaResponse(response.json())
                logger.debug(f"Comprobantes de venta: {len(comprobantes_venta_response.get_comprobantes())}")
                return comprobantes_venta_response.get_comprobantes()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting comprobantes de venta: {e}")
                return []

    async def get_comprobante_compra_details_by_id(self, empresa: Empresa, id_comprobante):
        comprobante_details_request = ComprobanteCompraDetailsRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token,
            id_empresa=empresa.id_empresa,
            id_comprobante=id_comprobante
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=comprobante_details_request.to_dict())
                response.raise_for_status()
                comprobante_details_response = ComprobanteCompraDetailsResponse(response.json())
                return comprobante_details_response.get_comprobante()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting comprobante details: {e}")
                return None

    async def get_comprobante_venta_details_by_id(self, empresa: Empresa, id_comprobante):
        comprobante_details_request = ComprobateVentaDetailsRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token,
            id_empresa=empresa.id_empresa,
            id_comprobante=id_comprobante
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=comprobante_details_request.to_dict())
                response.raise_for_status()
                comprobante_details_response = ComprobanteVentaDetailsResponse(response.json())
                return comprobante_details_response.get_comprobante()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting comprobante details: {e}")
                return None

    async def get_cobro_factura_by_id(self, empresa: Empresa, id_factura) -> list[CobroFactura]:
        cobro_factura_request = CobroFacturaRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token,
            id_empresa=empresa.id_empresa,
            id_factura=id_factura
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=cobro_factura_request.to_dict())
                response.raise_for_status()
                cobro_factura_response = CobroFacturaResponse(response.json())
                return cobro_factura_response.get_cobro()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting cobro factura: {e}")
                return []

    async def get_movimientos_by_empresa(self, empresa, from_date, to_date, start=0, limit=1000) -> list[Movimiento]:
        movimientos_request = MovimientosRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token,
            id_empresa=empresa.id_empresa,
            from_date=from_date,
            to_date=to_date,
            start=start,
            limit=limit
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=movimientos_request.to_dict(), timeout=240)
                response.raise_for_status()
                movimientos_response = MovimientosResponse(response.json())
                return movimientos_response.get_movimientos()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error al obtener movimientos: {e}")
                return []

    async def get_compras_pago_details_by_id_batch(self, id_pagos, empresa: Empresa):
        import pandas as pd
        all_pago_details = pd.DataFrame()

        async with httpx.AsyncClient(timeout=30.0) as client:
            for id_pago in id_pagos:
                compras_pago_request = ComprasPagoDetailsRequest(
                    auth_user=self._auth_user,
                    auth_password=self._auth_password,
                    params_user=self._params_user,
                    token=self._token,
                    id_pago=id_pago,
                    id_empresa=empresa.id_empresa
                )

                try:
                    response = await client.post(self._base_url, json=compras_pago_request.to_dict(), timeout=240)
                    response.raise_for_status()
                    compras_pago_response = ComprasPagoDetailsResponse(response.json())
                    logger.debug(
                        f"Detalles del pago {id_pago} para la empresa:{empresa}: {compras_pago_response.get_pago_details().to_dataframe()}")
                    pago_details = compras_pago_response.get_pago_details().to_dataframe()

                    if not pago_details.empty:
                        all_pago_details = pd.concat([all_pago_details, pago_details], ignore_index=True)
                except httpx.HTTPStatusError as e:
                    logger.error(f"Error al obtener detalles del pago {id_pago}: {e}")
                    continue

        return all_pago_details

    async def logout(self):
        logout_request = LogoutRequest(
            auth_user=self._auth_user,
            auth_password=self._auth_password,
            params_user=self._params_user,
            token=self._token
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self._base_url, json=logout_request.to_dict())
                response.raise_for_status()
                logout_response = LogoutResponse(response.json())
                logger.debug(f"Logout: {logout_response.get_logout()}")
                return logout_response.get_logout()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error logging out: {e}")
                return False
