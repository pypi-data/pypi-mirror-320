from typing import Optional
from pydantic import BaseModel
import time
import base64
import json
import asyncio
from urllib.parse import urlencode
from ..types import GlideSdkSettings, Session, ApiConfig, UserIdentifier, PhoneIdentifier, IpIdentifier, UserIdIdentifier
from ..utils import FetchError, fetch_x, FetchXInput, format_phone_number

class SimSwapCheckParams(BaseModel):
    phoneNumber: Optional[str] = None
    maxAge: Optional[int] = None

class SimSwapCheckResponse(BaseModel):
    swapped: bool

class SimSwapRetrieveDateParams(BaseModel):
    phoneNumber: Optional[str] = None

class SimSwapRetrieveDateResponse(BaseModel):
    latestSimChange: str

class SimSwapUserClient:
    def __init__(self, settings: GlideSdkSettings, identifier: UserIdentifier):
        self.settings = settings
        self.identifier = identifier
        self.session: Optional[Session] = None
        self.requires_consent = False
        self.consent_url: Optional[str] = None
        self.auth_req_id: Optional[str] = None

    def get_consent_url(self) -> str:
        return self.consent_url or ''

    async def check(self, params: Optional[SimSwapCheckParams] = None, conf: ApiConfig = ApiConfig()) -> SimSwapCheckResponse:
        if not self.settings.internal.apiBaseUrl:
            raise ValueError('[GlideClient] internal.apiBaseUrl is unset')

        if not (params and params.phoneNumber) and not isinstance(self.identifier, PhoneIdentifier):
            raise ValueError('[GlideClient] phone number not provided')

        phone_number = params.phoneNumber if params else self.identifier.phoneNumber

        try:
            session = conf.session or await self.get_session()
            data = {
                'phoneNumber': format_phone_number(phone_number)
            }
            if params and params.maxAge is not None:
                data['maxAge'] = params.maxAge

            response = await fetch_x(f"{self.settings.internal.apiBaseUrl}/sim-swap/check",
                                   FetchXInput(
                                       method='POST',
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {session.accessToken}'
                                       },
                                       body=json.dumps(data)
                                   ))

            if not response.ok:
                raise ValueError(f"Failed to resolve network id: {response.status}")

            return SimSwapCheckResponse(**response.json())

        except FetchError as e:
            if getattr(e.response, 'status', None) == 404:
                raise ValueError(f'[GlideClient] Network ID not found for number {phone_number}')
            raise e

    async def retrieve_date(self, params: Optional[SimSwapRetrieveDateParams] = None, conf: ApiConfig = ApiConfig()) -> SimSwapRetrieveDateResponse:
        if not self.settings.internal.apiBaseUrl:
            raise ValueError('[GlideClient] internal.apiBaseUrl is unset')

        if not (params and params.phoneNumber) and not isinstance(self.identifier, PhoneIdentifier):
            raise ValueError('[GlideClient] phone number not provided')

        phone_number = params.phoneNumber if params else self.identifier.phoneNumber

        try:
            session = conf.session or await self.get_session()
            response = await fetch_x(f"{self.settings.internal.apiBaseUrl}/sim-swap/retrieve-date",
                                   FetchXInput(
                                       method='POST',
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {session.accessToken}'
                                       },
                                       body=json.dumps({
                                           'phoneNumber': format_phone_number(phone_number)
                                       })
                                   ))

            if not response.ok:
                raise ValueError(f"Failed to resolve network id: {response.status}")

            return SimSwapRetrieveDateResponse(**response.json())

        except FetchError as e:
            if getattr(e.response, 'status', None) == 404:
                raise ValueError(f'[GlideClient] Network ID not found for number {phone_number}')
            raise e

    async def start_session(self):
        if not (self.settings.clientId and self.settings.clientSecret):
            raise ValueError('[GlideClient] Client credentials are required to generate a new session')

        try:
            auth = base64.b64encode(
                f"{self.settings.clientId}:{self.settings.clientSecret}".encode()
            ).decode()

            login_hint = None
            if isinstance(self.identifier, PhoneIdentifier):
                login_hint = f"tel:{format_phone_number(self.identifier.phoneNumber)}"
            elif not hasattr(self.identifier, 'userId'):
                login_hint = f"ipport:{self.identifier.ipAddress}"

            data = {'scope': 'sim-swap'}
            if login_hint:
                data['login_hint'] = login_hint

            response = await fetch_x(f"{self.settings.internal.authBaseUrl}/oauth2/backchannel-authentication",
                                   FetchXInput(
                                       method='POST',
                                       headers={
                                           'Content-Type': 'application/x-www-form-urlencoded',
                                           'Authorization': f'Basic {auth}'
                                       },
                                       body=urlencode(data)
                                   ))

            if not response.ok:
                raise ValueError(f"Failed to generate new session: {response.status}")

            body = response.json()
            if body.get('consentUrl'):
                self.requires_consent = True
                self.consent_url = body['consentUrl']
            self.auth_req_id = body['auth_req_id']

        except FetchError as e:
            if getattr(e.response, 'status', None) == 401:
                raise ValueError('[GlideClient] Invalid client credentials')
            elif getattr(e.response, 'status', None) == 400:
                data = json.loads(e.data)
                if data.get('error') == 'invalid_scope':
                    raise ValueError('[GlideClient] Client does not have required scopes to access this method')
                raise ValueError('[GlideClient] Invalid request')
            raise e

    async def get_session(self) -> Session:
        if (self.session and 
            self.session.expiresAt > (time.time() * 1000) + (60 * 1000) and 
            any(s.endswith('sim-swap') for s in self.session.scopes)):
            return self.session

        session = await self.generate_new_session()
        self.session = session
        self.auth_req_id = None
        return session

    async def poll_and_wait_for_session(self):
        while True:
            try:
                session = await self.get_session()
                if session:
                    return
            except Exception:
                await asyncio.sleep(5)

    async def generate_new_session(self) -> Session:
        if not (self.settings.clientId and self.settings.clientSecret):
            raise ValueError('[GlideClient] Client credentials are required to generate a new session')

        if not self.auth_req_id:
            await self.start_session()

        if not self.auth_req_id:
            raise ValueError('[GlideClient] Failed to start session')

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
                                           'grant_type': 'urn:openid:params:grant-type:ciba',
                                           'auth_req_id': self.auth_req_id
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
            self.auth_req_id = None
            if getattr(e.response, 'status', None) == 401:
                raise ValueError('[GlideClient] Invalid client credentials')
            elif getattr(e.response, 'status', None) == 400:
                data = json.loads(e.data)
                if data.get('error') == 'invalid_scope':
                    raise ValueError('[GlideClient] Client does not have required scopes to access this method')
                raise ValueError('[GlideClient] Invalid request')
            raise e

class SimSwapClient:
    settings: GlideSdkSettings

    def __init__(self, settings: GlideSdkSettings):
        self.settings = settings

    async def for_user(self, phone_number: str = None, ip_address: str = None, user_id: str = None) -> SimSwapUserClient:
        """Create a SimSwapUserClient for a specific identifier.
        
        Args:
            phone_number: Phone number to check
            ip_address: IP address to check
            user_id: User ID to check
            
        Returns:
            SimSwapUserClient instance
        """
        if phone_number:
            identifier = PhoneIdentifier(phoneNumber=phone_number)
        elif ip_address:
            identifier = IpIdentifier(ipAddress=ip_address)
        elif user_id:
            identifier = UserIdIdentifier(userId=user_id)
        else:
            raise ValueError("Must provide either phone_number, ip_address, or user_id")

        client = SimSwapUserClient(self.settings, identifier)
        await client.start_session()
        return client 