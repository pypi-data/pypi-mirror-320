import os
from dotenv import load_dotenv
from typing import Union, Dict, Any, Optional
from .types import GlideSdkSettings, PartialGlideSdkSettings, InternalSettings
from .services.telco_finder import TelcoFinderClient
from .services.magic_auth import MagicAuthClient
from .services.sim_swap import SimSwapClient
from .services.number_verify import NumberVerifyClient

class GlideClient:
    settings: GlideSdkSettings
    telco_finder: TelcoFinderClient
    magic_auth: MagicAuthClient
    sim_swap: SimSwapClient
    number_verify: NumberVerifyClient

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        use_env: Optional[bool] = None,
        auth_base_url: Optional[str] = None,
        api_base_url: Optional[str] = None
    ):
        if use_env is not False:
            load_dotenv()

        # Build settings from parameters or environment variables
        settings_dict = {
            'clientId': client_id or os.getenv('GLIDE_CLIENT_ID', ''),
            'clientSecret': client_secret or os.getenv('GLIDE_CLIENT_SECRET', ''),
            'redirectUri': redirect_uri or os.getenv('GLIDE_REDIRECT_URI', ''),
            'internal': {
                'authBaseUrl': auth_base_url or os.getenv('GLIDE_AUTH_BASE_URL', 'https://oidc.gateway-x.io'),
                'apiBaseUrl': api_base_url or os.getenv('GLIDE_API_BASE_URL', 'https://api.gateway-x.io')
            }
        }

        # Convert to GlideSdkSettings
        self.settings = GlideSdkSettings(**settings_dict)

        if not self.settings.clientId:
            raise ValueError('clientId is required')

        if not self.settings.internal.authBaseUrl:
            raise ValueError('internal.authBaseUrl is unset')

        # Initialize services
        self.telco_finder = TelcoFinderClient(self.settings)
        self.magic_auth = MagicAuthClient(self.settings)
        self.sim_swap = SimSwapClient(self.settings)
        self.number_verify = NumberVerifyClient(self.settings) 
