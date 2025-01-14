# Glide SDK for Python

A powerful Python SDK for integrating Glide's identity verification and fraud prevention services into your applications.

## Features

- **Magic Auth**: Passwordless authentication using phone numbers or email
- **Number Verification**: Verify phone numbers and detect potential fraud
- **SIM Swap Detection**: Check for recent SIM card changes to prevent fraud
- **Telco Finder**: Get detailed information about phone numbers' carriers

## Installation

```bash
pip install glide_sdk
```

## Quick Start

```python
# Example of using the Magical Auth
import asyncio
import httpx

from glide_sdk import GlideClient

async def main():
    # Initialize the client (will use .env)
    glide = GlideClient()
    
    # Start magic auth process
    magic_auth_start_response = await glide.magic_auth.start_auth(
        phone_number="+555123456789"
    )
    
    # Get token from auth URL
    async with httpx.AsyncClient(follow_redirects=True) as client:
        res = await client.get(magic_auth_start_response.authUrl)
        token = res.headers.get("token")
    
    # Verify the auth
    magic_auth_check_response = await glide.magic_auth.verify_auth(
        phone_number="+555123456789",
        token=token
    )
    print('Magic auth response:', magic_auth_check_response)

if __name__ == "__main__":
    asyncio.run(main()) 
```

## Features in Detail

### Magical Auth
Implement secure, passwordless authentication using phone numbers or email addresses. Supports:
- Phone number authentication
- Email authentication
- Custom redirect URLs
- Multiple verification channels

### Number Verification
Verify phone numbers and detect potential fraud with features like:
- Real-time number verification
- Fraud risk assessment
- Support for international numbers
- Hashed number verification

### SIM Swap Detection
Protect against SIM swap attacks with:
- Real-time SIM change detection
- Historical SIM change data
- Configurable detection windows

### Telco Finder
Get detailed carrier information:
- Carrier name and ID
- Country information
- MCC/MNC codes
- Network type detection

## Requirements

- Python 3.10 or higher
- `aiohttp` for async operations
- `requests` for HTTP operations
- Valid Glide API credentials

## Documentation

For detailed documentation, visit [https://docs.gateway-x.io/](https://docs.gateway-x.io/)

## License

MIT License
