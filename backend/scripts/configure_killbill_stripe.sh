#!/bin/bash
# Kill Bill Stripe Plugin Configuration Script
# This script configures Kill Bill to use your live Stripe API key

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== SOVREN Kill Bill Stripe Configuration ===${NC}"

# Check if environment variables are set
if [[ -z "$STRIPE_LIVE_SECRET_KEY" ]]; then
    echo -e "${RED}ERROR: STRIPE_LIVE_SECRET_KEY environment variable is not set${NC}"
    echo "Please set your Stripe live secret key:"
    echo "export STRIPE_LIVE_SECRET_KEY='sk_live_...'"
    exit 1
fi

if [[ -z "$STRIPE_LIVE_PUBLISHABLE_KEY" ]]; then
    echo -e "${RED}ERROR: STRIPE_LIVE_PUBLISHABLE_KEY environment variable is not set${NC}"
    echo "Please set your Stripe live publishable key:"
    echo "export STRIPE_LIVE_PUBLISHABLE_KEY='pk_live_...'"
    exit 1
fi

# Kill Bill configuration
KILLBILL_URL="${KILLBILL_URL:-http://localhost:8080}"
KILLBILL_API_KEY="${KILLBILL_API_KEY:-sovren}"
KILLBILL_API_SECRET="${KILLBILL_API_SECRET:-sovren123}"
TENANT_API_KEY="${KILLBILL_TENANT_API_KEY:-sovren_tenant}"
TENANT_API_SECRET="${KILLBILL_TENANT_API_SECRET:-sovren_tenant_secret}"

echo -e "${YELLOW}Configuring Kill Bill with 