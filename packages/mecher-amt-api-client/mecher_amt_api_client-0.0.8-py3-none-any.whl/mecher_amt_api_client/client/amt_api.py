from mecher_amt_api_client.client.endpoints.app_artefact import AppArtefact_Api
from mecher_amt_api_client.client.endpoints.app_run_config import AppRunConfig_Api
from mecher_amt_api_client.client.endpoints.auth import Auth_Api
from mecher_amt_api_client.client.endpoints.bs_owner import BSOwner_Api
from mecher_amt_api_client.models.amt_user import AMT_User_Auth


class AMT_Api(
    AppArtefact_Api,
    AppRunConfig_Api,
    BSOwner_Api,
    Auth_Api,
):
    def __init__(self, user: AMT_User_Auth):
        super().__init__()

        try:
            login_response = self.login(user)
            headers = {f"Authorization": f"Bearer {login_response['access_token']}"}
            self.default_headers_set = self._build_request_headers(headers)
        except KeyError:
            raise Exception("Login failed. Please check your credentials.")
