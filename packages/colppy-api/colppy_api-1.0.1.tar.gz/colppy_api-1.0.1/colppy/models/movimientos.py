from dataclasses import dataclass, field

from colppy.helpers.errors import ColppyError
from colppy.helpers.formatters import BaseModel


@dataclass(init=False)
class Movimiento(BaseModel):
    id_empresa: str = field(metadata={"alias": "idEmpresa"}, default=None)
    id_tabla: int = field(metadata={"alias": "idTabla"}, default=0)
    id_elemento: int = field(metadata={"alias": "idElemento"}, default=0)
    id_diario: int = field(metadata={"alias": "idDiario"}, default=0)
    id_elemento_contacto: int = field(metadata={"alias": "idElementoContacto"}, default=0)
    id_objeto_contacto: int = field(metadata={"alias": "idObjetoContacto"}, default=0)
    fecha_contabilizado: str = field(metadata={"alias": "FechaContabilizado"}, default=None)
    fecha_contable: str = field(metadata={"alias": "fechaContable"}, default=None)
    id_plan_cuenta: int = field(metadata={"alias": "idPlanCuenta"}, default=0)
    id_subdiario: int = field(metadata={"alias": "idSubdiario"}, default=0)
    debito_credito: str = field(metadata={"alias": "DebitoCredito"}, default=None)
    importe: float = field(metadata={"alias": "Importe"}, default=0.0)
    id_tabla_aplicado: int = field(metadata={"alias": "idTablaAplicado"}, default=0)
    id_elemento_aplicado: int = field(metadata={"alias": "idElementoAplicado"}, default=0)
    id_item: int = field(metadata={"alias": "idItem"}, default=0)
    id_item_aplicado: int = field(metadata={"alias": "idItemAplicado"}, default=0)
    ccosto1: str = field(metadata={"alias": "ccosto1"}, default=None)
    ccosto2: str = field(metadata={"alias": "ccosto2"}, default=None)
    conciliado: str = field(metadata={"alias": "Conciliado"}, default=None)
    batch: str = field(metadata={"alias": "batch"}, default=None)
    id_tercero: int = field(metadata={"alias": "idTercero"}, default=0)
    is_niif: str = field(metadata={"alias": "isNIIF"}, default=None)
    item_id: int = field(metadata={"alias": "itemId"}, default=0)


class MovimientosRequest:
    def __init__(self, auth_user, auth_password, params_user, token, id_empresa, from_date, to_date, start=0,
                 limit=1000):
        self._auth_user = auth_user
        self._auth_password = auth_password
        self._params_user = params_user
        self._token = token
        self._id_empresa = id_empresa
        self._from_date = from_date
        self._to_date = to_date
        self._start = start
        self._limit = limit

    def to_dict(self):
        return {
            "auth": {
                "usuario": self._auth_user,
                "password": self._auth_password
            },
            "service": {
                "provision": "Contabilidad",
                "operacion": "listar_movimientosdiario"
            },
            "parameters": {
                "sesion": {
                    "usuario": self._params_user,
                    "claveSesion": self._token
                },
                "idEmpresa": self._id_empresa,
                "fromDate": self._from_date,
                "toDate": self._to_date,
                "start": self._start,
                "limit": self._limit,
            }
        }


class MovimientosResponse:
    def __init__(self, response):
        self._response = response

    def get_movimientos(self):
        if not ColppyError(self._response).is_error():
            if self._response['response']['movimientos']:
                return [Movimiento(**movimiento) for movimiento in self._response['response']['movimientos']]

        return []
