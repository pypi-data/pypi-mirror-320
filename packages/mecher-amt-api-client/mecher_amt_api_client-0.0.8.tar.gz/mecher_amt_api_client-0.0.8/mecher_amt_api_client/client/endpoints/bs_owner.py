import allure

from mecher_amt_api_client.amt_api_common import AMT_ApiCommon
from mecher_amt_api_client.models.browserstack_owner import BrowserstackOwner


class BSOwner_Api(AMT_ApiCommon):
    def __init__(self):
        super().__init__()
        self.browserstack_owner_url = self.url + "/browserstack_owner"

    def get_bs_owner(self, bs_owner: str) -> BrowserstackOwner | None:
        with allure.step('AMT API: Get Browserstack Owner'):
            response = self.send_request(method='get',
                                         params={'bs_owner': bs_owner},
                                         uri=self.browserstack_owner_url)
            if response.status_code == 200:
                return BrowserstackOwner(**response.json())
            else:
                return
