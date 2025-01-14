from uiaccessclient.openapi import *
from uiaccessclient.websocket import *

class ApiClient(ApiClient):
    def __init__(self, hostname, access_token):
        configuration = Configuration(
            f"https://{hostname}:12445/api/v1/developer",
            access_token=access_token
        )
        configuration.verify_ssl = False
        super().__init__(configuration)