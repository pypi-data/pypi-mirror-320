from typing import Optional

from pydantic import BaseModel
from starlette.datastructures import UploadFile

from mecher_amt_api_client.models.app_run_config import DEFAULT_APP_FORMAT


class AppArtefact__Upload(BaseModel):
    bs_owner: str
    project: str
    version: str = DEFAULT_APP_FORMAT
    tag: Optional[str] = ''

    platform: Optional[str]
    extension: Optional[str]
    file_name: Optional[str]


class AppArtefact__With_File(AppArtefact__Upload):
    file: UploadFile


class AppArtefact__Read(AppArtefact__Upload):
    bs_app_url: str
    bs_app_name: str

    class Config:
        openapi_example = {
            "example": {
                "summary": "example_uploaded_app",
                "value": {
                    "bs_owner": "mecher",
                    "project": "project",
                    "version": DEFAULT_APP_FORMAT,
                    "tag": "",
                    "platform": "ios",
                    "extension": "ipa",
                    "file_name": "file_name.ipa",
                    "bs_app_url": "https://app-url.com",
                    "bs_app_name": "app_name",
                }
            }
        }

    @staticmethod
    def default_instance() -> 'AppArtefact__Read':
        return AppArtefact__Read(**AppArtefact__Read.Config.openapi_example['example']['value'])


class AppArtefact__Search(BaseModel):
    project: str
    bs_owner: str
    platform: str
    version: str = DEFAULT_APP_FORMAT
    tag: str = ''

    class Config:
        openapi_example = {
            "example": {
                "summary": "example_app_for_search",
                "value": {
                    "project": "project",
                    "bs_owner": "mecher",
                    "platform": "ios",
                    "version": DEFAULT_APP_FORMAT,
                    "tag": ""
                }
            }
        }

    @staticmethod
    def default_instance() -> 'AppArtefact__Search':
        return AppArtefact__Search(**AppArtefact__Search.Config.openapi_example['example']['value'])
