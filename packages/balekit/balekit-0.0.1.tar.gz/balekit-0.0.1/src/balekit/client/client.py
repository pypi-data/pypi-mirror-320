import requests
import json
from .methods import getMe, sendMessage

class Bot(getMe, sendMessage):
    def __init__(
            self,
            token: str,
            base_url: str = "https://tapi.bale.ai"
            ):
        self.token = token
        self.url = f"{base_url}/bot{str(token)}/"
    
    def send_request(self, method, **kwargs):
        res = self.url + method
        req = requests.get(res,params=kwargs)
        return req.json()
