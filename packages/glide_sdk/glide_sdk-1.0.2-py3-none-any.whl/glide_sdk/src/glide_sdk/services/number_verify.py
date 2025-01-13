from typing import Optional
from pydantic import BaseModel
import uuid
from urllib.parse import urlencode
import base64
import json
import time
from ..types import GlideSdkSettings, Session, ApiConfig
from ..utils import fetch_x, FetchXInput

class NumberVerifyAuthUrlInput(BaseModel):
    state: Optional[str] = None
    useDevNumber: Optional[str] = None
    printCode: Optional[bool] = None

class NumberVerifyClientForParams(BaseModel):
    code: str
    phoneNumber: Optional[str] = None

class NumberVerifyInput(BaseModel):
    phoneNumber: Optional[str] = None

class NumberVerifyResponse(BaseModel):
    devicePhoneNumberVerified: bool

class NumberVerifyUserClient:
    def __init__(self, settings: GlideSdkSettings, params: NumberVerifyClientForParams):
        self.settings = settings
        self.code = params.code
        self.phoneNumber = params.phoneNumber
        self.session: Optional[Session] = None

    async def start_session(self):
        if not self.settings.internal.authBaseUrl:
            raise ValueError('[GlideClient] internal.authBaseUrl is unset')

        if not (self.settings.clientId and self.settings.clientSecret):
            raise ValueError('[GlideClient] Client credentials are required to generate a new session')

        if not self.code:
            raise ValueError('[GlideClient] Code is required to start a session')

        try:
            auth = base64.b64encode(
                f"{self.settings.clientId}:{self.settings.clientSecret}".encode()
            ).decode()

            response = await fetch_x(f"{self.settings.internal.authBaseUrl}/oauth2/token",
                                   FetchXInput(
                                       method='POST',
                                       headers={
                                           'Content-Type': 'application/x-www-form-urlencoded',
                                           'Authorization': f'Basic {auth}'
                                       },
                                       body=urlencode({
                                           'grant_type': 'authorization_code',
                                           'code': self.code
                                       })
                                   ))

            if not response.ok:
                raise ValueError(f"Failed to generate new session: {response.status}")

            body = response.json()
            self.session = Session(
                accessToken=body['access_token'],
                expiresAt=int(time.time() * 1000) + (body['expires_in'] * 1000),
                scopes=body['scope'].split(' ')
            )

        except Exception as e:
            raise e

    async def get_operator(self) -> str:
        if not self.session:
            raise ValueError('[GlideClient] Session is required to get operator')

        token = self.session.accessToken
        try:
            parsed_token = base64.b64decode(token.split('.')[1] + '==').decode()
            token_data = json.loads(parsed_token)
            return token_data['ext']['operator']
        except Exception as e:
            print(f"Error: {e}")
            return 'unknown'

    async def verify_number(self, input_data: NumberVerifyInput = NumberVerifyInput(), conf: ApiConfig = ApiConfig()) -> NumberVerifyResponse:
        if not self.session:
            raise ValueError('[GlideClient] Session is required to verify a number')

        if not self.settings.internal.apiBaseUrl:
            raise ValueError('[GlideClient] internal.apiBaseUrl is unset')

        phone_number = input_data.phoneNumber or self.phoneNumber
        if not phone_number:
            raise ValueError('[GlideClient] Phone number is required to verify a number')

        try:
            session = conf.session or self.session
            response = await fetch_x(f"{self.settings.internal.apiBaseUrl}/number-verification/verify",
                                   FetchXInput(
                                       method='POST',
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {session.accessToken}'
                                       },
                                       body=json.dumps({
                                           'phoneNumber': phone_number
                                       })
                                   ))

            if not response.ok:
                raise ValueError(f"Failed to verify number: {response.status}")

            return NumberVerifyResponse(**response.json())

        except Exception as e:
            raise e

class NumberVerifyClient:
    def __init__(self, settings: GlideSdkSettings):
        self.settings = settings

    async def get_auth_url(
        self,
        use_dev_number: Optional[str] = None,
        print_code: Optional[bool] = None,
        state: Optional[str] = None
    ) -> str:
        """Get authentication URL for number verification.
        
        Args:
            use_dev_number: Phone number to use for development/testing
            print_code: Whether to print the verification code
            state: Optional state parameter
            
        Returns:
            Authentication URL
        """
        if not self.settings.internal.authBaseUrl:
            raise ValueError('[GlideClient] internal.authBaseUrl is unset')
        if not self.settings.clientId:
            raise ValueError('[GlideClient] Client id is required to generate an auth url')

        # Convert to proper type
        input_data = NumberVerifyAuthUrlInput(
            useDevNumber=use_dev_number,
            printCode=print_code,
            state=state
        )

        state = input_data.state or str(uuid.uuid4())
        nonce = str(uuid.uuid4())

        params = {
            'client_id': self.settings.clientId,
            'response_type': 'code',
            'scope': 'openid',
            'purpose': 'dpv:FraudPreventionAndDetection:number-verification',
            'state': state,
            'nonce': nonce,
            'max_age': '0'
        }

        if self.settings.redirectUri:
            params['redirect_uri'] = self.settings.redirectUri
        if input_data.printCode:
            params['dev_print'] = 'true'
        if input_data.useDevNumber:
            params['login_hint'] = f"tel:{input_data.useDevNumber}"

        return f"{self.settings.internal.authBaseUrl}/oauth2/auth?{urlencode(params)}"

    async def for_user(
        self,
        code: str,
        phone_number: Optional[str] = None
    ) -> NumberVerifyUserClient:
        """Create a NumberVerifyUserClient for a specific user.
        
        Args:
            code: Authorization code
            phone_number: Optional phone number
            
        Returns:
            NumberVerifyUserClient instance
        """
        # Convert to proper type
        params = NumberVerifyClientForParams(
            code=code,
            phoneNumber=phone_number
        )
        
        client = NumberVerifyUserClient(self.settings, params)
        await client.start_session()
        return client 