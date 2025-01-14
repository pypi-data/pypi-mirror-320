import json
import requests

from pydantic import BaseModel

from pkg.models import RequestData, ResponseData

class GetDatabaseService(BaseModel):
    base_url: str

    def get_database(self, nb_agente_comercial) -> ResponseData:
        url = self.base_url
        empresa = RequestData(empresa=nb_agente_comercial)
        req_body = json.dumps(empresa.model_dump())

        try:
            response = requests.post(url=url, headers={"Content-Type": "application/json"}, data=req_body)
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"HTTP Request failed: {e}")

        try:
            response_data = response.json()
            return ResponseData(content=response_data.get("content"), iv=response_data.get("iv"))
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to decode JSON response: {e}")
