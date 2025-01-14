from pydantic import BaseModel

from .pkg.decrypt import DecryptService
from .pkg.get_database import GetDatabaseService

from .pkg.models import DatabaseConnectionGerencia

class GerenciaDecrypt(BaseModel):
    nb_agente_comercial: str = None
    get_database_service: GetDatabaseService = None
    decrypt_service: DecryptService = None
    base_url: str = None
    key: str = None

    def model_post_init(self, __context):
        self.get_database_service = GetDatabaseService(base_url=self.base_url)
        self.decrypt_service = DecryptService(key=self.key)

    def do(self) -> DatabaseConnectionGerencia:
        response_data = self.get_database_service.get_database(nb_agente_comercial=self.nb_agente_comercial)
        return self.decrypt_service.decrypt(data=response_data)
