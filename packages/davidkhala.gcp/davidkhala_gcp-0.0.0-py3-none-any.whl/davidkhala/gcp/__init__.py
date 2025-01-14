from dataclasses import dataclass
from typing import TypedDict, NotRequired

import google.auth
from google.oauth2 import service_account, credentials


@dataclass
class ServiceAccountInfo(TypedDict):
    client_email: str
    private_key: str
    token_uri: NotRequired[str]
    project_id: NotRequired[str]


class AuthOptions:
    credentials: service_account.Credentials | credentials.Credentials
    """
    :type credentials: service_account.Credentials | credentials.Credentials
    being as google.oauth2.credentials.Credentials when get from Application Default Credentials (ADC)
    raw secret not cached in credentials object. You need cache it by yourself.  
    """
    projectId: str

    @staticmethod
    def default():
        c = AuthOptions()
        c.credentials, c.projectId = google.auth.default()
        return c

    @staticmethod
    def from_service_account(info: ServiceAccountInfo = None, *, client_email, private_key, project_id):
        if not info:
            info = {
                'client_email': client_email,
                'private_key': private_key,
            }
        if project_id:
            info['project_id'] = project_id

        info['token_uri'] = "https://oauth2.googleapis.com/token"

        c = AuthOptions()
        c.credentials = service_account.Credentials.from_service_account_info(info)
        c.projectId = info['project_id']
        return c
