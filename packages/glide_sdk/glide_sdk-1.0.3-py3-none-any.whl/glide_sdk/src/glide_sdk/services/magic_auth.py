from typing import Optional, Literal, Union, Dict, Any
from pydantic import BaseModel
from enum import Enum
from ..types import GlideSdkSettings, Session, ApiConfig
from ..utils import FetchError, fetch_x, FetchXInput
import json
import time
import base64
from urllib.parse import urlencode

class FallbackVerificationChannel(str, Enum):
    SMS = 'SMS'
    EMAIL = 'EMAIL'
    NO_FALLBACK = 'NO_FALLBACK'

class BaseMagicAuthStartProps(BaseModel):
    fallbackChannel: Optional[FallbackVerificationChannel] = None

class MagicAuthStartPropsEmail(BaseMagicAuthStartProps):
    email: str

class MagicAuthStartPropsPhone(BaseMagicAuthStartProps):
    phoneNumber: str
    redirectUrl: Optional[str] = None
    state: Optional[str] = None

MagicAuthStartProps = Union[MagicAuthStartPropsEmail, MagicAuthStartPropsPhone]

class MagicAuthStartCodeResponse(BaseModel):
    type: Literal['EMAIL', 'SMS']

class MagicAuthStartMagicResponse(BaseModel):
    type: Literal['MAGIC']
    authUrl: str
    flatAuthUrl: str
    operatorId: str

MagicAuthStartResponse = Union[MagicAuthStartCodeResponse, MagicAuthStartMagicResponse]

class MagicAuthVerifyEmailProps(BaseModel):
    email: str
    code: str

class MagicAuthVerifyPhoneProps(BaseModel):
    phoneNumber: str
    code: str

class MagicAuthVerifyMagicProps(BaseModel):
    phoneNumber: str
    token: str

MagicAuthVerifyProps = Union[MagicAuthVerifyEmailProps, MagicAuthVerifyPhoneProps, MagicAuthVerifyMagicProps]

class MagicAuthCheckResponse(BaseModel):
    verified: bool

class MagicAuthClient:
    def __init__(self, settings: GlideSdkSettings):
        self.settings = settings
        self.session: Optional[Session] = None

    async def start_auth(self, **kwargs) -> MagicAuthStartResponse:
        """Start magic auth process.
        
        Args:
            phone_number: Phone number for authentication
            email: Email for authentication
            fallback_channel: Optional fallback channel (SMS, EMAIL, NO_FALLBACK)
            redirect_url: Optional redirect URL
            state: Optional state parameter
            
        Returns:
            MagicAuthStartResponse
        """
        if not self.settings.internal.apiBaseUrl:
            raise ValueError('[GlideClient] internal.apiBaseUrl is unset')
        
        try:
            session = await self.get_session()

            # Convert snake_case to camelCase for props
            props_dict = {
                'phoneNumber': kwargs.get('phone_number'),
                'email': kwargs.get('email'),
                'fallbackChannel': kwargs.get('fallback_channel'),
                'redirectUrl': kwargs.get('redirect_url'),
                'state': kwargs.get('state')
            }

            # Remove None values
            props_dict = {k: v for k, v in props_dict.items() if v is not None}

            # Create appropriate props object
            if 'phoneNumber' in props_dict:
                props = MagicAuthStartPropsPhone(**props_dict)
            elif 'email' in props_dict:
                props = MagicAuthStartPropsEmail(**props_dict)
            else:
                raise ValueError("Must provide either phone_number or email")

            response = await fetch_x(f"{self.settings.internal.apiBaseUrl}/magic-auth/verification/start",
                                   FetchXInput(
                                       method='POST',
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {session.accessToken}'
                                       },
                                       body=json.dumps(props.model_dump(exclude_none=True))
                                   ))

            if not response.ok:
                raise ValueError(f"Failed to start auth: {response.status}")

            data = response.json()
            if data.get('type') == 'MAGIC':
                return MagicAuthStartMagicResponse(**data)
            return MagicAuthStartCodeResponse(**data)

        except Exception as e:
            raise e

    async def verify_auth(self, **kwargs) -> MagicAuthCheckResponse:
        """Verify magic auth.
        
        Args:
            phone_number: Phone number used for authentication
            email: Email used for authentication
            token: Magic link token
            code: Verification code
            
        Returns:
            MagicAuthCheckResponse
        """
        if not self.settings.internal.apiBaseUrl:
            raise ValueError('[GlideClient] internal.apiBaseUrl is unset')

        try:
            session = await self.get_session()

            # Convert snake_case to camelCase for props
            props_dict = {
                'phoneNumber': kwargs.get('phone_number'),
                'email': kwargs.get('email'),
                'token': kwargs.get('token'),
                'code': kwargs.get('code')
            }

            # Remove None values
            props_dict = {k: v for k, v in props_dict.items() if v is not None}

            # Create appropriate props object
            if 'phoneNumber' in props_dict:
                if 'token' in props_dict:
                    props = MagicAuthVerifyMagicProps(**props_dict)
                else:
                    props = MagicAuthVerifyPhoneProps(**props_dict)
            elif 'email' in props_dict:
                props = MagicAuthVerifyEmailProps(**props_dict)
            else:
                raise ValueError("Must provide either phone_number or email")

            response = await fetch_x(f"{self.settings.internal.apiBaseUrl}/magic-auth/verification/check",
                                   FetchXInput(
                                       method='POST',
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {session.accessToken}'
                                       },
                                       body=json.dumps(props.model_dump(exclude_none=True))
                                   ))

            if not response.ok:
                raise ValueError(f"Failed to verify auth: {response.status}")

            return MagicAuthCheckResponse(**response.json())

        except Exception as e:
            raise e

    async def get_session(self) -> Session:
        if (self.session and 
            self.session.expiresAt > (time.time() * 1000) + (60 * 1000) and 
            'magic-auth' in self.session.scopes):
            return self.session
        
        session = await self.generate_new_session()
        self.session = session
        return session

    async def generate_new_session(self) -> Session:
        if not (self.settings.clientId and self.settings.clientSecret):
            raise ValueError('[GlideClient] Client credentials are required to generate a new session')
        
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
                                           'grant_type': 'client_credentials',
                                           'scope': 'magic-auth'
                                       })
                                   ))
            
            if not response.ok:
                raise ValueError(f"Failed to generate new session: {response.status}")
            
            body = response.json()
            return Session(
                accessToken=body['access_token'],
                expiresAt=int(time.time() * 1000) + (body['expires_in'] * 1000),
                scopes=body['scope'].split(' ')
            )

        except FetchError as e:
            if getattr(e.response, 'status', None) == 401:
                raise ValueError('[GlideClient] Invalid client credentials')
            elif getattr(e.response, 'status', None) == 400:
                data = json.loads(e.data)
                if data.get('error') == 'invalid_scope':
                    raise ValueError('[GlideClient] Client does not have required scopes to access this method')
                raise ValueError('[GlideClient] Invalid request')
            raise e 