from mecher_base_api_client.api_client import API


class AMT_ApiCommon(API):
    def __init__(self):
        super().__init__(url='http://0.0.0.0:8080/api',
                         default_status_codes=(200, 201, 204),
                         timeout=100)

    def send_request(self, uri: str, **kwargs):
        response = self.send_request_base(url=uri, **kwargs)
        return response
