import sys
import os
import asyncio
import httpx

# Add the local src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from glide_sdk import GlideClient

PHONE_NUMBER = "+555123456789"

async def main():
    # Initialize the client (will use .env)
    glide = GlideClient()
    
    # Start magic auth process
    magic_auth_start_response = await glide.magic_auth.start_auth(
        phone_number=PHONE_NUMBER
    )
    print('Magic auth start response:', magic_auth_start_response)
    
    # Get token from auth URL
    async with httpx.AsyncClient(follow_redirects=True) as client:
        res = await client.get(magic_auth_start_response.authUrl)
        token = res.headers.get("token")
    
    # Verify the auth
    magic_auth_check_response = await glide.magic_auth.verify_auth(
        phone_number=PHONE_NUMBER,
        token=token
    )
    print('Magic auth response:', magic_auth_check_response)

if __name__ == "__main__":
    asyncio.run(main()) 