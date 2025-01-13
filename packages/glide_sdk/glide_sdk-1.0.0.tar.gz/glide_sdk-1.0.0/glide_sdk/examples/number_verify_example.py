import sys
import os
import asyncio
import httpx

# Add the local src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from glide_sdk import GlideClient

async def main():
    # Initialize the client (will use .env)
    glide = GlideClient()
    
    phone_number = '+555123456789'
    
    # Get authentication URL with dev number and print code options
    auth_url = await glide.number_verify.get_auth_url(
        use_dev_number=phone_number,
        print_code=True
    )
    
    # Make request to get the code
    async with httpx.AsyncClient(follow_redirects=True) as client:
        res = await client.get(auth_url)
        code = res.json()['code']
    
    # Create user client with code and phone number
    user_client = await glide.number_verify.for_user(
        code=code,
        phone_number=phone_number
    )
    
    # Verify the phone number
    verification_res = await user_client.verify_number()
    print(verification_res)

if __name__ == "__main__":
    asyncio.run(main()) 