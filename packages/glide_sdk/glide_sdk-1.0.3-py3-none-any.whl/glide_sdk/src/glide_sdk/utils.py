import re
import json
import aiohttp
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse

class Response:
    def __init__(self, data: str, status: int, ok: bool):
        self._data = data
        self.status = status
        self.ok = ok

    def json(self) -> Any:
        return json.loads(self._data)

    def text(self) -> str:
        return self._data

class FetchError(Exception):
    def __init__(self, status: int, status_msg: str, data: str):
        super().__init__(f"Fetch Error: {status} {status_msg}")
        self.status = status
        self.status_msg = status_msg
        self.data = data

class FetchXInput:
    def __init__(self, method: str, headers: Dict[str, str], body: Optional[str] = None):
        self.method = method
        self.headers = headers
        self.body = body

async def fetch_x(url: str, input: FetchXInput) -> Response:
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=input.method,
            url=url,
            headers=input.headers,
            data=input.body
        ) as response:
            data = await response.text()
            
            if response.status >= 400:
                raise FetchError(response.status, response.reason, data)
            
            return Response(data, response.status, response.status < 400)

def format_phone_number(phone_number: str) -> str:
    return f"+{re.sub(r'[^0-9]', '', phone_number)}" 