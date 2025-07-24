#!/usr/bin/env python3
"""
Admin Stripe Configuration for Kill Bill
One-time setup for admin to configure Kill Bill with Stripe API key
"""

import os
import sys
import getpass
import base64
import json
import aiohttp
import asyncio
from pathlib import Path

def secure_input(prompt: str) -> str:
    """Get secure input without echoing"""
    return getpass.getpass(prompt)

def validate_stripe_key(key: str) -> bool:
    """Validate Stripe key format"""
    if not key:
        return False
    
    if key.startswith('sk_live_') and len(key) > 20:
        return True
    elif key.startswith('pk_live_') and len(key) > 20:
        return True
    else:
        return False

async def admin_configure_stripe():
    """One-time admin configuration of Kill Bill with Stripe"""
    
    print("=== SOVREN ADMIN: Kill Bill Stripe Configuration ===")
    print("This is a ONE-TIME setup for the admin only.")
    print("After this, all users will use the configured Stripe integration.")
    print()
    
    # Get Kill Bill admin credentials
    print("Kill Bill Admin Configuration:")
    killbill_url = input("Kill Bill URL [http://localhost:8080]: ").strip() or "http://localhost:8080"
    admin_username = input("Kill Bill Admin Username: ").strip()
    admin_password = secure_input("Kill Bill Admin Password: ")
    
    if not admin_username or not admin_password:
        print("❌ Admin credentials are required")
        return False
    
    print()
    print("Stripe Configuration:")
    print("⚠️  WARNING: You are about to configure LIVE Stripe API keys")
    print("   This will be stored securely in Kill Bill's database")
    print()
    
    # Get Stripe keys
    stripe_secret_key = secure_input("Stripe Live Secret Key (sk_live_...): ")
    if not validate_stripe_key(stripe_secret_key):
        print("❌ Invalid Stripe secret key format")
        return False
    
    stripe_publishable_key = secure_input("Stripe Live Publishable Key (pk_live_...): ")
    if not validate_stripe_key(stripe_publishable_key):
        print("❌ Invalid Stripe publishable key format")
        return False
    
    stripe_webhook_secret = secure_input("Stripe Webhook Secret (whsec_...) [optional]: ")
    
    print()
    print("Configuring Kill Bill with Stripe...")
    
    # Create admin auth headers
    credentials = f"{admin_username}:{admin_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Test Kill Bill connectivity
            print("1. Testing Kill Bill connectivity...")
            async with session.get(f"{killbill_url}/1.0/kb/healthcheck", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Kill Bill not accessible: {response.status}")
                    return False
                print("✅ Kill Bill is accessible")
            
            # Step 2: Install Stripe plugin
            print("2. Installing Stripe plugin...")
            plugin_data = {
                "plugin_name": "killbill-stripe",
                "version": "0.1.0",
                "plugin_type": "PAYMENT",
                "plugin_info": {
                    "properties": [
                        {
                            "key": "org.killbill.billing.plugin.stripe.api_key",
                            "value": stripe_secret_key
                        },
                        {
                            "key": "org.killbill.billing.plugin.stripe.publishable_key",
                            "value": stripe_publishable_key
                        },
                        {
                            "key": "org.killbill.billing.plugin.stripe.currency",
                            "value": "USD"
                        }
                    ]
                }
            }
            
            if stripe_webhook_secret:
                plugin_data["plugin_info"]["properties"].append({
                    "key": "org.killbill.billing.plugin.stripe.webhook_secret",
                    "value": stripe_webhook_secret
                })
            
            async with session.post(f"{killbill_url}/1.0/kb/plugins", headers=headers, json=plugin_data) as response:
                if response.status in [200, 201, 409]:  # 409 means already installed
                    print("✅ Stripe plugin configured")
                else:
                    error = await response.text()
                    print(f"❌ Failed to configure plugin: {error}")
                    return False
            
            # Step 3: Configure payment methods
            print("3. Configuring payment methods...")
            payment_method_data = {
                "pluginName": "killbill-stripe",
                "pluginInfo": {
                    "properties": [
                        {
                            "key": "payment_method_type",
                            "value": "card"
                        }
                    ]
                }
            }
            
            async with session.post(f"{killbill_url}/1.0/kb/accounts/1/paymentMethods", headers=headers, json=payment_method_data) as response:
                if response.status in [200, 201]:
                    print("✅ Payment methods configured")
                else:
                    print(f"⚠️  Payment method configuration returned: {response.status}")
            
            # Step 4: Create SOVREN subscription plans
            print("4. Creating SOVREN subscription plans...")
            
            plans = [
                {
                    "product": "SOVREN_PROOF",
                    "productCategory": "BASE",
                    "billingPeriod": "MONTHLY",
                    "price": 497.00,
                    "currency": "USD",
                    "name": "SOVREN Proof (Monthly)"
                },
                {
                    "product": "SOVREN_PROOF",
                    "productCategory": "BASE", 
                    "billingPeriod": "YEARLY",
                    "price": 5367.00,
                    "currency": "USD",
                    "name": "SOVREN Proof (Yearly)"
                },
                {
                    "product": "SOVREN_PROOF_PLUS",
                    "productCategory": "BASE",
                    "billingPeriod": "MONTHLY", 
                    "price": 797.00,
                    "currency": "USD",
                    "name": "SOVREN Proof+ (Monthly)"
                },
                {
                    "product": "SOVREN_PROOF_PLUS",
                    "productCategory": "BASE",
                    "billingPeriod": "YEARLY",
                    "price": 8607.00,
                    "currency": "USD", 
                    "name": "SOVREN Proof+ (Yearly)"
                }
            ]
            
            for plan in plans:
                async with session.post(f"{killbill_url}/1.0/kb/catalog/simplePlan", headers=headers, json=plan) as response:
                    if response.status in [200, 201]:
                        print(f"✅ Created plan: {plan['name']}")
                    else:
                        print(f"⚠️  Plan creation returned: {response.status} for {plan['name']}")
            
            print()
            print("=== CONFIGURATION COMPLETE ===")
            print("✅ Kill Bill is now configured with your Stripe API key")
            print("✅ All future billing operations will use this configuration")
            print("✅ No users will need to enter API keys")
            print()
            print("Next steps:")
            print("1. Test a payment in Kill Bill admin interface")
            print("2. Monitor Stripe dashboard for transactions")
            print("3. Set up webhook endpoints if needed")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during configuration: {e}")
        return False

if __name__ == "__main__":
    print("ADMIN ONLY: This script configures Kill Bill with your Stripe API key")
    print("This is a one-time setup. After this, all users will use the configured system.")
    print()
    
    response = input("Continue with admin configuration? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled")
        sys.exit(0)
    
    asyncio.run(admin_configure_stripe()) 