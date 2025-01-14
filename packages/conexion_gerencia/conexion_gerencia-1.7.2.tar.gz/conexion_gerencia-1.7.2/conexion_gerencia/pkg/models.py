from pydantic import BaseModel


class RequestData(BaseModel):
    empresa: str

class ResponseData(BaseModel):
    content: str
    iv: str

class DatabaseConnectionGerencia(BaseModel):
    host: str
    port: int
    bd: str