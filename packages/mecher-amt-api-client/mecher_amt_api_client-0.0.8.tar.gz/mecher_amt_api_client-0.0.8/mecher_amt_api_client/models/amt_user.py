from enum import Enum

from pydantic import BaseModel


class Roles(Enum):
    ADMIN = 'admin'
    MORTAL = 'mortal'

    @staticmethod
    def get_all_roles():
        return [role for role in Roles]


class AMT_User_Auth(BaseModel):
    username: str
    password: str

    class Config:
        openapi_example = {
            "example": {
                "summary": "example_user",
                "value": {
                    "username": "mecher",
                    "password": "123"
                }
            }
        }

    @staticmethod
    def default_instance() -> 'AMT_User_Auth':
        return AMT_User_Auth(**AMT_User_Auth.Config.openapi_example['example']['value'])


class AMT_User(AMT_User_Auth):
    role: Roles
    enabled: bool = True

    class Config:
        openapi_example = {
            "example": {
                "summary": "example_user",
                "value": {
                    **AMT_User_Auth.Config.openapi_example['example']['value'],
                    "role": Roles.MORTAL,
                    "enabled": True
                }
            }
        }

    @staticmethod
    def default_instance() -> 'AMT_User':
        return AMT_User(**AMT_User.Config.openapi_example['example']['value'])


class UserToken(BaseModel):
    username: str
    expires: int

    class Config:
        openapi_example = {
            "example": {
                "summary": "example_user",
                "value": {
                    "username": "username",
                    "expires": 161354390
                }
            }
        }

    @staticmethod
    def default_instance() -> 'UserToken':
        return UserToken(**UserToken.Config.openapi_example['example']['value'])
