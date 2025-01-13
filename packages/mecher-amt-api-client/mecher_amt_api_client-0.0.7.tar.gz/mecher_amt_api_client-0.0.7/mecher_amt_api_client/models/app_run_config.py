from pydantic import BaseModel

DEFAULT_APP_FORMAT = 'v0_0_1'


class AppRunConfig(BaseModel):
    name: str = 'project__mecher__ios__iphone_12__14_4__v0_0_1__v0_0_1'
    bs_owner: str = 'mecher'
    project: str = 'project'
    platform: str = 'ios'
    device: str = 'iPhone 14'
    platform_version: str = '15'
    app_version: str = DEFAULT_APP_FORMAT
    tag: str = ''
    locators_version: str = DEFAULT_APP_FORMAT
    locators_comment: str = ''

    class Config:
        openapi_example = {
            "iOS Example": {
                "summary": "Example of AppRunConfig for iOS",
                "value": {
                    "name": "project__mecher__ios__iphone_12__14_4__v0_0_1__v0_0_1",
                    "bs_owner": "mecher",
                    "project": "project",
                    "platform": "ios",
                    "device": "iPhone 13",
                    "platform_version": "15",
                    "app_version": DEFAULT_APP_FORMAT,
                    "tag": "",
                    "locators_version": DEFAULT_APP_FORMAT,
                    "locators_comment": ""
                }
            },
            "Android Example": {
                "summary": "Example of AppRunConfig for Android",
                "value": {
                    "name": "project__mecher__ios__iphone_12__14_4__v0_0_1__v0_0_1",
                    "bs_owner": "mecher",
                    "project": "project",
                    "platform": "android",
                    "device": "Google Pixel 7",
                    "platform_version": "13.0",
                    "app_version": DEFAULT_APP_FORMAT,
                    "tag": "",
                    "locators_version": DEFAULT_APP_FORMAT,
                    "locators_comment": ""
                }
            }
        }

    @staticmethod
    def default_ios_instance() -> 'AppRunConfig':
        return AppRunConfig(**AppRunConfig.Config.openapi_example['iOS Example']['value'])

    @staticmethod
    def default_android_instance() -> 'AppRunConfig':
        return AppRunConfig(**AppRunConfig.Config.openapi_example['Android Example']['value'])


class AppRunConfig_WithBSInfo(AppRunConfig):
    bs_app_url: str
    bs_app_name: str
