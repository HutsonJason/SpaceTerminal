from requests.auth import AuthBase
from requests_ratelimiter import LimiterSession


class BearerAuth(AuthBase):
    """Attaches Bearer Access Token to the given Request object."""

    def __init__(self, access_token):
        self.access_token = access_token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.access_token}"
        return r


class Client:
    """Holds the account access token and session for API calls."""

    def __init__(self, access_token: str = None):
        self.access_token = access_token

    @property
    def auth(self):
        return BearerAuth(self.access_token)

    @property
    def session(self):
        s = LimiterSession(limit_statuses=[429, 502], per_second=2, burst=10)
        # This check is needed for registering new account, the POST can't use auth.
        if self.access_token is not None:
            s.auth = self.auth
        s.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        return s

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        self._access_token = access_token
