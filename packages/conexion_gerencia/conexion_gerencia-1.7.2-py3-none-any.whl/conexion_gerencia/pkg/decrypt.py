import json
import base64

from pydantic import BaseModel

from Crypto.Cipher import AES

from .models import DatabaseConnectionGerencia, ResponseData

class DecryptService(BaseModel):
    key: str

    def decrypt(self, data: ResponseData) -> DatabaseConnectionGerencia:
        try:
            ciphertext = base64.b64decode(data.content)
            iv = data.iv.encode()

            cipher = AES.new(self.key.encode(), AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)

            unpadding = decrypted[-1]
            decrypted = decrypted[:-unpadding].decode()

            database_connection = json.loads(decrypted)
            return DatabaseConnectionGerencia(
                host=database_connection["host"],
                port=database_connection["port"],
                bd=database_connection["bd"]
            )

        except (base64.binascii.Error, KeyError, ValueError, json.JSONDecodeError) as e:
            raise Exception(f"Decryption failed: {e}")
