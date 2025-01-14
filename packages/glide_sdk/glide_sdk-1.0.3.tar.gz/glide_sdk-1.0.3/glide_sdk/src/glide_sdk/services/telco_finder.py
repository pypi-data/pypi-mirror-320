from typing import Optional
import time
import base64
import json
from urllib.parse import urlencode
from ..types import GlideSdkSettings, Session, ApiConfig, TelcoFinderNetworkIdResponse, TelcoFinderSearchResponse
from ..utils import FetchError, fetch_x, FetchXInput, format_phone_number

class TelcoFinderClient:
    def __init__(self, settings: GlideSdkSettings):
        self.settings = settings
        self.session: Optional[Session] = None

    async def network_id_for_number(self, phone_number: str, conf: ApiConfig = ApiConfig()) -> TelcoFinderNetworkIdResponse:
        if not self.settings.internal.apiBaseUrl:
            raise ValueError('[GlideClient] internal.apiBaseUrl is unset')

        try:
            session = conf.session or await self.get_session()
            response = await fetch_x(f"{self.settings.internal.apiBaseUrl}/telco-finder/v1/resolve-network-id",
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

            return TelcoFinderNetworkIdResponse(**response.json())

        except FetchError as e:
            if getattr(e.response, 'status', None) == 404:
                raise ValueError(f'[GlideClient] Network ID not found for number {phone_number}')
            raise e

    async def lookup_ip(self, ip: str, conf: ApiConfig = ApiConfig()) -> TelcoFinderSearchResponse:
        return await self.lookup(subject=f"ipport:{ip}", conf=conf)

    async def lookup_number(self, phone_number: str, conf: ApiConfig = ApiConfig()) -> TelcoFinderSearchResponse:
        return await self.lookup(subject=f"tel:{format_phone_number(phone_number)}", conf=conf)

    async def lookup(self, subject: str, conf: ApiConfig = ApiConfig()) -> TelcoFinderSearchResponse:
        if not self.settings.internal.apiBaseUrl:
            raise ValueError('[GlideClient] internal.apiBaseUrl is unset')

        try:
            session = conf.session or await self.get_session()
            response = await fetch_x(f"{self.settings.internal.apiBaseUrl}/telco-finder/v1/search",
                                   FetchXInput(
                                       method='POST',
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': f'Bearer {session.accessToken}'
                                       },
                                       body=json.dumps({
                                           'resource': subject
                                       })
                                   ))

            if not response.ok:
                raise ValueError(f"Failed to lookup telco: {response.status}")

            res_obj = response.json()
            if 'properties' in res_obj and 'operator_Id' in res_obj['properties']:
                res_obj['properties']['operatorId'] = res_obj['properties'].pop('operator_Id')
            return TelcoFinderSearchResponse(**res_obj)

        except FetchError as e:
            if getattr(e.response, 'status', None) == 404:
                raise ValueError(f'[GlideClient] Lookup failed for subject {subject}')
            raise e

    async def get_session(self) -> Session:
        if (self.session and 
            self.session.expiresAt > (time.time() * 1000) + (60 * 1000) and 
            'telco-finder' in self.session.scopes):
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
                                           'scope': 'telco-finder'
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