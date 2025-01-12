import os

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse

from fastapi_booster import settings
from fastapi_booster.Module import Module


class OAuthenticator(Module):
    """
    OAuth authentication module for FastAPI Booster.

    This class provides OAuth-based authentication functionality for FastAPI applications.
    It implements a singleton pattern and handles OAuth authentication flows including
    login, authentication, and logout.

    Attributes:
        _instance (OAuthenticator): Singleton instance of the OAuthenticator class
        oauth (OAuth): OAuth client instance for handling authentication

    Configuration:
        OAUTH_SERVER_CONFIG_URL (str): URL for OAuth server configuration
        OAUTH_CLIENT_ID (str): OAuth client ID
        OAUTH_CLIENT_SECRET (str): OAuth client secret
        OAUTH_CLIENT_KWARGS (dict): Additional OAuth client configuration (default: {"scope": "openid email profile"})
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of OAuthenticator if it doesn't exist, otherwise return the existing instance.

        This method implements the Singleton pattern for the OAuthenticator class.

        Returns:
            OAuthenticator: The single instance of the OAuthenticator class
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of the OAuthenticator class.

        Returns:
            OAuthenticator: The single instance of the OAuthenticator class
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """
        Initialize the OAuth authentication module.

        Sets up the OAuth client with configuration from environment variables
        and registers the default OAuth provider.
        """
        super().__init__("OAuth", "OAuth Authenticator")

        self.oauth = OAuth()
        self.oauth.register(
            name="default",
            server_metadata_url=settings.OAUTH_SERVER_CONFIG_URL,
            client_id=settings.OAUTH_CLIENT_ID,
            client_secret=settings.OAUTH_CLIENT_SECRET,
            client_kwargs=settings.OAUTH_CLIENT_KWARGS,
        )

    def __call__(self, request: Request):
        user = request.session.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


oauth_instance = OAuthenticator.get_instance()


@oauth_instance.router.get("/login")
async def login(request: Request):
    """
    Initiate the OAuth login flow.

    Redirects the user to the OAuth provider's authorization endpoint.

    Args:
        request (Request): The incoming request object

    Returns:
        Response: Redirect response to the OAuth provider's authorization endpoint
    """
    redirect_uri = request.url_for("auth")
    return await oauth_instance.oauth.default.authorize_redirect(request, redirect_uri)  # type: ignore


@oauth_instance.router.get("/auth")
async def auth(request: Request):
    """
    Handle the OAuth callback and complete the authentication flow.

    Processes the OAuth callback, retrieves the access token and user information,
    and stores the user data in the session.

    Args:
        request (Request): The incoming request object

    Returns:
        HTMLResponse: Success or error message

    Raises:
        OAuthError: If the OAuth authentication process fails
    """
    try:
        token = await oauth_instance.oauth.authentik.authorize_access_token(request)  # type: ignore
    except OAuthError as error:
        return HTTPException(status_code=401, detail=error.error)
    user = token.get("userinfo")
    if user:
        request.session["user"] = dict(user)
    return HTMLResponse(status_code=200, content="Login successful")


@oauth_instance.router.get("/logout")
async def logout(request: Request):
    """
    Log out the current user.

    Removes the user information from the session.

    Args:
        request (Request): The incoming request object

    Returns:
        HTMLResponse: Success message indicating successful logout
    """
    request.session.pop("user", None)
    return HTMLResponse(status_code=200, content="Logout successful")

