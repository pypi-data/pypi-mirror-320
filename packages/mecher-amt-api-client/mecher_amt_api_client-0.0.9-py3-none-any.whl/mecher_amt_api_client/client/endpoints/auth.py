import allure

from mecher_amt_api_client.amt_api_common import AMT_ApiCommon
from mecher_amt_api_client.models.amt_user import AMT_User_Auth


class Auth_Api(AMT_ApiCommon):
    def __init__(self):
        super().__init__()
        self.auth_url = self.url + "/auth"

    def login(self, user: AMT_User_Auth):
        uri = self.auth_url + "/login"
        with allure.step('AMT API: Login'):
            response = self.send_request(method='post',
                                         body=user.dict(),
                                         uri=uri)
            if response.status_code == 200:
                return response.json()
            else:
                return
