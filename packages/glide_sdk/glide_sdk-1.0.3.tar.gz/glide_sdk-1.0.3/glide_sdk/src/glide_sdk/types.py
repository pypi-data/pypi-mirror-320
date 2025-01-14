from typing import Optional, Dict, List, Union
from pydantic import BaseModel

class InternalSettings(BaseModel):
    authBaseUrl: str
    apiBaseUrl: str

class GlideSdkSettings(BaseModel):
    clientId: str
    clientSecret: str
    redirectUri: str
    useEnv: Optional[bool] = None
    internal: InternalSettings

class PartialInternalSettings(BaseModel):
    authBaseUrl: Optional[str] = None
    apiBaseUrl: Optional[str] = None

class PartialGlideSdkSettings(BaseModel):
    clientId: Optional[str] = None
    clientSecret: Optional[str] = None
    redirectUri: Optional[str] = None
    useEnv: Optional[bool] = None
    internal: Optional[PartialInternalSettings] = None

class Session(BaseModel):
    accessToken: str
    expiresAt: int
    scopes: List[str]

class ApiConfig(BaseModel):
    session: Optional[Session] = None

# Telco Finder
class TelcoFinderNetworkIdResponse(BaseModel):
    networkId: str

class TelcoFinderSearchProperties(BaseModel):
    operatorId: str

class TelcoFinderSearchLink(BaseModel):
    rel: str
    href: str

class TelcoFinderSearchResponse(BaseModel):
    subject: str
    properties: TelcoFinderSearchProperties
    links: List[TelcoFinderSearchLink]

class PhoneIdentifier(BaseModel):
    phoneNumber: str

class IpIdentifier(BaseModel):
    ipAddress: str

class UserIdIdentifier(BaseModel):
    userId: str

UserIdentifier = Union[PhoneIdentifier, IpIdentifier, UserIdIdentifier] 