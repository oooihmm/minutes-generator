import os
import json
import requests
from dotenv import load_dotenv


class PapagoTranslator:
    def __init__(self, url: str="https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"):
        load_dotenv()
        
        self._client_id = os.getenv("PAPAGO_CLIENT_ID", "")
        self._client_secret = os.getenv("PAPAGO_CLIENT_SECRET", "")
        self.url = url

    def translate_minute(self, summary: str):
        _headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-NCP-APIGW-API-KEY-ID": self._client_id,
        "X-NCP-APIGW-API-KEY": self._client_secret,
        }

        data = {'source':'en', 'target':'ko', 'text': summary}
        
        response = requests.post(self.url, headers=_headers, data=data)
        response_json = response.json()

        if "error" in response_json.keys():
            # result = response_json["error"]["message"]
            return False
        else: 
            result = response_json["message"]["result"]["translatedText"]
            return result