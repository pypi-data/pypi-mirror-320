import re
from typing import Optional

from fastapi import UploadFile, HTTPException
from pydantic import BaseModel
from starlette import status

from app.core.constants import DEFAULT_APP_FORMAT
from tests.constants import DEBUG_TAG_FOR_UNIT_TESTS


class AppArtefact__Upload(BaseModel):
    bs_owner: str
    project: str
    version: str = DEFAULT_APP_FORMAT
    tag: Optional[str] = ''

    platform: Optional[str]
    extension: Optional[str]
    file_name: Optional[str]

    def build_file_name(self):
        if self.tag == DEBUG_TAG_FOR_UNIT_TESTS:  # we need this workaround for unit tests
            self.file_name = DEBUG_TAG_FOR_UNIT_TESTS
        else:
            self.file_name = f'{self.project}__{self.bs_owner}__{self.platform}__{self.version}__{self.tag}.{self.extension}'


class AppArtefact__With_File(AppArtefact__Upload):
    file: UploadFile

    def determine_platform(self):
        if self.file.filename.endswith('.apk'):
            self.extension = 'apk'
            self.platform = 'android'
        elif self.file.filename.endswith('.ipa'):
            self.extension = 'ipa'
            self.platform = 'ios'
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Unknown file extension. Only .apk and .ipa are allowed: {self.file.filename}')

    def check_version_format(self):
        pattern = r'^v\d+_\d+_\d+$'
        if not re.match(pattern, DEFAULT_APP_FORMAT):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Invalid re-expression: {pattern} for expected format: {DEFAULT_APP_FORMAT}')

        if not re.match(pattern, self.version):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Invalid version format: {self.version}. Expected format: {DEFAULT_APP_FORMAT}')


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
