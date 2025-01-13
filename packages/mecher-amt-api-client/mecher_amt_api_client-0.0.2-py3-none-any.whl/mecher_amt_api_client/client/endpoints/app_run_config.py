import allure

from mecher_amt_api_client.amt_api_common import AMT_ApiCommon
from mecher_amt_api_client.models.app_run_config import AppRunConfig


class AppRunConfig_Api(AMT_ApiCommon):
    def __init__(self):
        super().__init__()
        self.app_run_config_url = self.url + "/app_run_config"

    def upload_app_run_config(self, app_run_config: AppRunConfig) -> AppRunConfig | None:
        with allure.step('AMT API: Upload App Run Config'):
            response = self.send_request(method='post',
                                         body=app_run_config.dict(),
                                         uri=self.app_run_config_url)
            if response.status_code == 200:
                return AppRunConfig(**response)
            else:
                return

    def get_app_run_config(self, app_run_config_data: AppRunConfig) -> AppRunConfig | None:
        uri = self.app_run_config_url + "/uploaded"

        with allure.step('AMT API: Get App Run Config'):
            response = self.send_request(method='post',
                                         body=app_run_config_data.dict(),
                                         uri=uri)
            if response.status_code == 200:
                return AppRunConfig(**response)
            else:
                return
