#!/usr/bin/env python3
"""
SOVREN Billing System - Deployment Script
Production deployment with health checks and monitoring
"""

import os
import sys
import asyncio
import logging
import signal
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from billing_integration import initialize_billing, get_billing_system, BillingSystem

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('billing_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('BillingDeployment')

class BillingDeployment:
    """Production deployment manager for billing system"""
    
    def __init__(self):
        self.billing_system: Optional[BillingSystem] = None
        self.running = False
        self.health_check_interval = 30  # seconds
        self.max_retries = 3
        
    async def initialize(self) -> bool:
        """Initialize the billing system"""
        try:
            logger.info("Initializing SOVREN Billing System...")
            
            # Check environment variables
            self._validate_environment()
            
            # Initialize billing system
            self.billing_system = await initialize_billing()
            
            # Perform health check
            if await self._health_check():
                logger.info("Billing system initialized successfully")
                return True
            else:
                logger.error("Health check failed during initialization")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize billing system: {e}")
            return False
    
    def _validate_environment(self):
        """Validate required environment variables"""
        required_vars = [
            'KILLBILL_API_KEY',
            'KILLBILL_API_SECRET',
            'WEBHOOK_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")
            logger.info("Using default values for development")
    
    async def _health_check(self) -> bool:
        """Perform health check on billing system"""
        try:
            if not self.billing_system:
                return False
            
            # Test basic functionality
            metrics = self.billing_system.get_billing_metrics()
            
            # Verify metrics structure
            required_keys = ['customers', 'revenue', 'subscriptions', 'churn_rate', 'usage']
            for key in required_keys:
                if key not in metrics:
                    logger.error(f"Missing metric key: {key}")
                    return False
            
            logger.info("Health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def start(self):
        """Start the billing system deployment"""
        logger.info("Starting SOVREN Billing System deployment...")
        
        # Initialize system
        if not await self.initialize():
            logger.error("Failed to initialize billing system")
            sys.exit(1)
        
        self.running = True
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Billing system is running. Press Ctrl+C to stop.")
        
        try:
            # Main deployment loop
            while self.running:
                # Perform periodic health checks
                if not await self._health_check():
                    logger.error("Health check failed, attempting recovery...")
                    await self._recover()
                
                # Wait for next health check
                await asyncio.sleep(self.health_check_interval)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error in deployment loop: {e}")
        finally:
            await self.shutdown()
    
    async def _recover(self):
        """Attempt to recover from failures"""
        logger.info("Attempting system recovery...")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Recovery attempt {attempt + 1}/{self.max_retries}")
                
                # Reinitialize system
                if await self.initialize():
                    logger.info("Recovery successful")
                    return
                
                await asyncio.sleep(5 * (attempt + 1))  # Exponential backoff
                
            except Exception as e:
                logger.error(f"Recovery attempt {attempt + 1} failed: {e}")
        
        logger.error("All recovery attempts failed")
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def shutdown(self):
        """Shutdown the billing system"""
        logger.info("Shutting down billing system...")
        
        if self.billing_system:
            try:
                await self.billing_system.shutdown()
                logger.info("Billing system shutdown complete")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
        
        logger.info("Deployment stopped")

async def run_deployment():
    """Run the billing system deployment"""
    deployment = BillingDeployment()
    await deployment.start()

def main():
    """Main entry point"""
    try:
        # Check if running in production mode
        if os.getenv('PRODUCTION_MODE', 'false').lower() == 'true':
            logger.info("Running in PRODUCTION mode")
        else:
            logger.info("Running in DEVELOPMENT mode")
        
        # Run deployment
        asyncio.run(run_deployment())
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 