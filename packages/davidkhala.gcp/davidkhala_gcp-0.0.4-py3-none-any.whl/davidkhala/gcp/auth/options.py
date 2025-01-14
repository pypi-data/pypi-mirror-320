import google.auth
from google.oauth2 import service_account, credentials

from davidkhala.gcp.auth import ServiceAccountInfo


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
    def from_service_account(info: ServiceAccountInfo = None, *, client_email, private_key, project_id=None):
        if not info:
            info = {
                'client_email': client_email,
                'private_key': private_key,
            }
        if project_id:
            info['project_id'] = project_id

        if not info.get('project_id'):
            info['project_id'] = info.get('client_email').split('@')[1].split('.')[0]

        info['token_uri'] = "https://oauth2.googleapis.com/token"

        c = AuthOptions()
        c.credentials = service_account.Credentials.from_service_account_info(info)
        c.projectId = info['project_id']
        return c
