import time
import calendar
import ldt_identity_client
from ldt_identity_client import PostSessionRequest


PROD_LOGIN_HOST = "https://gotlivedata.io/api/identity/v1"
STAGING_LOGIN_HOST = "https://staging.gotlivedata.io/api/identity/v1"

class ServiceAccountClient:
    def __init__(self, client_id: str, client_secret: str, environment: str = "production") -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._expires_at = None
        self._is_logging_in = False

        grant_type = "clientCredentials"
        if self.client_id.startswith("isa_"):
            grant_type = "internalClient"       

        self.payload:PostSessionRequest = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": grant_type
        }             

        identity_client = self.setup_identity_client(environment)
        self.identity_api = ldt_identity_client.SessionApi(identity_client)

    def _active(self):
        if not self._access_token:
            return False

        if not self._expires_at:
            return False

        now = time.time()
        will_expire_soon = self._expires_at - now < 25

        if will_expire_soon:
            return False

        return True
    
    def setup_identity_client(self, env: str):
        if env == "staging":
            configuration = ldt_identity_client.Configuration(host=STAGING_LOGIN_HOST)
        else:
            configuration = ldt_identity_client.Configuration(host=PROD_LOGIN_HOST)

        return ldt_identity_client.ApiClient(configuration)    

    def access_token(self) -> str:
        if self._is_logging_in:
            for i in range(25):
                time.sleep(0.5)

                if not self._is_logging_in:
                    break

        if not self._active():
            self.login()

        return self._access_token

    def login(self) -> str:
        self._is_logging_in = True

        resp = self.identity_api.post_session(self.payload, _request_timeout=10)

        self._access_token = resp.get('accessToken')
        self._expires_at = int(
            calendar.timegm(
                time.strptime(resp.get('expiresAt'), "%Y-%m-%dT%H:%M:%S.%f")))
        
        self._is_logging_in = False
