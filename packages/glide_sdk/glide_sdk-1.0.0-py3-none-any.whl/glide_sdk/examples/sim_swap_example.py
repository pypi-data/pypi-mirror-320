import sys
import os
import asyncio

# Add the local src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from glide_sdk import GlideClient

async def main():
    # Initialize the client with simple parameters
    glide = GlideClient()
    
    # Create a sim swap client for a specific phone number
    sim_swap_client = await glide.sim_swap.for_user(
        phone_number="+555123456789"
    )
    
    # Check for SIM swap
    sim_swap_res = await sim_swap_client.check()
    print(sim_swap_res)

if __name__ == "__main__":
    asyncio.run(main()) 