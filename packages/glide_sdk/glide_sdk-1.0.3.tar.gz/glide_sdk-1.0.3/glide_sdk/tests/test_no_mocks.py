import pytest
from glide_sdk import GlideClient
from glide_sdk.types import PartialGlideSdkSettings

@pytest.mark.asyncio
async def test_sim_swap_check():
    # Initialize the client with default settings (will use .env)
    glide = GlideClient(PartialGlideSdkSettings())
    
    # Create a sim swap client for a specific phone number
    sim_swap_client = await glide.sim_swap.for_user({
        "phoneNumber": "+555123456789"
    })
    
    # Check for SIM swap
    sim_swap_res = await sim_swap_client.check()
    
    # Basic assertions to ensure we got a response
    assert sim_swap_res is not None
    assert hasattr(sim_swap_res, "swapped")
    print(f"SIM swap result: {sim_swap_res}")
