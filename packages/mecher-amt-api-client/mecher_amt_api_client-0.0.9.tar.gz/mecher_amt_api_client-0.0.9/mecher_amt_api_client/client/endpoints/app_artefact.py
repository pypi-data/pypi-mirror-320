from pathlib import Path

import allure

from mecher_amt_api_client.amt_api_common import AMT_ApiCommon
from mecher_amt_api_client.models.app_artefact import AppArtefact__Read, AppArtefact__Search


class AppArtefact_Api(AMT_ApiCommon):
    def __init__(self):
        super().__init__()
        self.app_artefact_url = self.url + "/app_artefact"

    def upload_app_artefact(self,
                            file_path: str,
                            project: str,
                            bs_owner: str = 'mecher',
                            version: str = 'v0_0_1'
                            ) -> AppArtefact__Read | None:
        with allure.step('AMT API: Upload App Artefact'):
            multipart_form_data = {
                'file': (f'{Path(file_path).name}', open(file_path, 'rb')),
            }
            params = {
                'project': project,
                'bs_owner': bs_owner,
                'version': version,
            }
            response = self.send_request(method='post',
                                         files=multipart_form_data,
                                         params=params,
                                         uri=self.app_artefact_url)
            if response.status_code == 200:
                return AppArtefact__Read(**response.json())
            else:
                return

    def get_app_artefact(self, app_artefact_for_search: AppArtefact__Search) -> AppArtefact__Read | None:
        uri = self.app_artefact_url + "/uploaded"

        with allure.step('AMT API: Get App Artefact'):
            response = self.send_request(method='post',
                                         body=app_artefact_for_search.dict(),
                                         uri=uri)
            if response.text != 'null' and response.status_code == 200:
                return AppArtefact__Read(**response.json())
            else:
                return
