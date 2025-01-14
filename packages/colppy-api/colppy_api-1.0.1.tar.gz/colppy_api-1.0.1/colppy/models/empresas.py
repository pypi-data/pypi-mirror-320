from dataclasses import dataclass, field

from colppy.helpers.errors import ColppyError
from colppy.helpers.formatters import BaseModel


@dataclass(init=False)
class Empresa(BaseModel):
    id_empresa: int = field(metadata={'alias': 'IdEmpresa', "primary_key": True})
    razon_social: str = field(metadata={'alias': 'razonSocial'}, default=None)
    nombre: str = field(metadata={'alias': 'Nombre'}, default=None)
    id_plan: str = field(metadata={'alias': 'idPlan', 'to_sql': False}, default=None)
    tipo: str = field(metadata={'alias': 'tipo', 'to_sql': False}, default=None)
    es_administrador: str = field(metadata={'alias': 'esAdministrador', 'to_sql': False}, default=None)
    logo_path: str = field(metadata={'alias': 'logoPath', 'to_sql': False}, default=None)
    activa: int = field(metadata={'alias': 'activa'}, default=0)
    fecha_vencimiento: str = field(metadata={'alias': 'fechaVencimiento', 'to_sql': False}, default=None)
    ultimo_login: str = field(metadata={'alias': 'UltimoLogin', 'to_sql': False}, default=None)
    cuit: str = field(metadata={'alias': 'CUIT'}, default=None)
    fecha_cierre_impuesto: str = field(metadata={'alias': 'fecha_cierre_impuesto', 'to_sql': False}, default=None)
    actividad_economica: str = field(metadata={'alias': 'actividad_economica', 'to_sql': False}, default=None)


class EmpresasRequest:
    def __init__(self, auth_user, auth_password, params_user, token, filters=None, start=0, limit=100):
        self._auth_user = auth_user
        self._auth_password = auth_password
        self._params_user = params_user
        self._token = token
        self._start = start
        self._limit = limit
        self._filters = filters if filters else []

    def to_dict(self):
        return {
            "auth": {
                "usuario": self._auth_user,
                "password": self._auth_password
            },
            "service": {
                "provision": "Empresa",
                "operacion": "listar_empresa"
            },
            "parameters": {
                "sesion": {
                    "usuario": self._params_user,
                    "claveSesion": self._token
                },
                "start": self._start,
                "limit": self._limit,
                "filter": self._filters
            }
        }


class EmpresasResponse:
    def __init__(self, response):
        self._response = response

    def get_empresas(self):
        if not ColppyError(self._response).is_error():
            if self._response['response']['data']:
                return [Empresa(**empresa) for empresa in self._response['response']['data']]
        return []
