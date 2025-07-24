#!/usr/bin/env python3
"""
Verify Stripe Configuration in Kill Bill
Check that the admin configuration is working correctly
"""

import asyncio
import aiohttp
import base64

async def verify_stripe_config():
    """Verify that Stripe is properly configured in Kill Bill"""
    
    print("=== Verifying Stripe Configuration ===")
    
    # Get configuration
    killbill_url = input("Kill Bill URL [http://localhost:8080]: ").strip() or "http://localhost:8080"
    admin_username = input("Kill Bill Admin Username: ").strip()
    admin_password = input("Kill Bill Admin Password: ").strip()
    
    # Create auth headers
    credentials = f"{admin_username}:{admin_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Kill Bill connectivity
            print("1. Testing Kill Bill connectivity...")
            async with session.get(f"{killbill_url}/1.0/kb/healthcheck", headers=headers) as response:
                if response.status == 200:
                    print("   ✓ Kill Bill is accessible")
                else:
                    print(f"   ✗ Kill Bill returned status {response.status}")
                    return False
            
            # Test 2: Check Stripe plugin
            print("2. Checking Stripe plugin...")
            async with session.get(f"{killbill_url}/1.0/kb/plugins", headers=headers) as response:
                if response.status == 200:
                    plugins = await response.json()
                    stripe_plugin = next((p for p in plugins if 'stripe' in p.get('plugin_name', '').lower()), None)
                    if stripe_plugin:
                        print("   ✓ Stripe plugin is installed")
                    else:
                        print("   ✗ Stripe plugin not found")
                        return False
                else:
                    print(f"   ✗ Failed to get plugins: {response.status}")
                    return False
            
            # Test 3: Check payment methods
            print("3. Checking payment methods...")
            async with session.get(f"{killbill_url}/1.0/kb/accounts/1/paymentMethods", headers=headers) as response:
                if response.status == 200:
                    payment_methods = await response.json()
                    if payment_methods:
                        print("   ✓ Payment methods configured")
                    else:
                        print("   ⚠ No payment methods found")
                else:
                    print(f"   ✗ Failed to get payment methods: {response.status}")
            
            print("\n=== Verification Complete ===")
            print("✓ Kill Bill is running and accessible")
            print("✓ Stripe plugin is installed")
            print("\nNext steps:")
            print("1. Create a test customer in Kill Bill")
            print("2. Test a payment using the Stripe plugin")
            print("3. Monitor logs for any issues")
            
            return True
            
    except Exception as e:
        print(f"✗ Error during verification: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(verify_stripe_config())