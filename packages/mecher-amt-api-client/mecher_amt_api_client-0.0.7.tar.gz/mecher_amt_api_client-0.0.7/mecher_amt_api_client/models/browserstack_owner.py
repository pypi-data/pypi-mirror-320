from pydantic import BaseModel


class BrowserstackOwner(BaseModel):
    user_name: str
    access_key: str
    bs_owner: str = 'mecher'

    class Config:
        openapi_example = {
            "example": {
                "summary": "example_bs_owner",
                "value": {
                    "user_name": "example_user",
                    "access_key": "example_key",
                    "bs_owner": "mecher"
                }
            }
        }

    @staticmethod
    def default_instance() -> 'BrowserstackOwner':
        return BrowserstackOwner(**BrowserstackOwner.Config.openapi_example['example_user']['value'])
