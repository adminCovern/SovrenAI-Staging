#!/usr/bin/env python3
"""
SOVREN AI Bayesian Engine Deployment Script
Handles production deployment with validation and monitoring
"""

import os
import sys
import subprocess
import argparse
import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sovren-bayesian-deploy')

class BayesianEngineDeployer:
    """Deployment manager for Bayesian Engine"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.engine = None
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load deployment configuration"""
        default_config = {
            'num_gpus': 0,
            'db_path': '/data/sovren/bayesian/decisions.db',
            'log_level': 'INFO',
            'test_mode': False,
            'monitoring_enabled': True
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def validate_environment(self) -> bool:
        """Validate deployment environment"""
        logger.info("Validating deployment environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8+ required")
            return False
        
        # Check dependencies
        required_packages = ['numpy', 'sqlite3']
        optional_packages = ['torch']
        
        missing_required = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_required.append(package)
        
        if missing_required:
            logger.error(f"Missing required packages: {missing_required}")
            return False
        
        # Check optional packages
        missing_optional = []
        for package in optional_packages:
            try:
                __import__(package)
            except ImportError:
                missing_optional.append(package)
        
        if missing_optional:
            logger.warning(f"Missing optional packages: {missing_optional}")
        
        # Check database directory
        db_dir = os.path.dirname(self.config['db_path'])
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
            except Exception as e:
                logger.error(f"Failed to create database directory: {e}")
                return False
        
        # Check write permissions
        if not os.access(db_dir, os.W_OK):
            logger.error(f"No write permission for database directory: {db_dir}")
            return False
        
        logger.info("Environment validation passed")
        return True
    
    def run_tests(self) -> bool:
        """Run comprehensive test suite"""
        logger.info("Running test suite...")
        
        try:
            # Run unit tests
            result = subprocess.run([
                sys.executable, 'test_bayesian_engine.py'
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode != 0:
                logger.error(f"Tests failed:\n{result.stderr}")
                return False
            
            logger.info("All tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return False
    
    def deploy_engine(self) -> bool:
        """Deploy the Bayesian engine"""
        logger.info("Deploying Bayesian engine...")
        
        try:
            from bayesian_engine import BayesianEngine
            
            # Initialize engine
            self.engine = BayesianEngine(
                num_gpus=self.config['num_gpus'],
                db_path=self.config['db_path']
            )
            
            # Run deployment test
            if self.config['test_mode']:
                self._run_deployment_test()
            
            logger.info("Engine deployment successful")
            return True
            
        except Exception as e:
            logger.error(f"Engine deployment failed: {e}")
            return False
    
    def _run_deployment_test(self):
        """Run deployment validation test"""
        logger.info("Running deployment test...")
        
        from bayesian_engine import Decision
        
        # Create test decision
        test_decision = Decision(
            decision_id="deployment_test",
            context={"test": True, "deployment": "validation"},
            options=["pass", "fail"],
            constraints={},
            universes_to_simulate=2
        )
        
        # Make test decision
        if self.engine is None:
            raise Exception("Engine not initialized")
        
        result = self.engine.make_decision(test_decision)
        
        # Validate result
        if not result or 'selected_option' not in result:
            raise Exception("Deployment test failed - invalid result")
        
        logger.info(f"Deployment test passed - selected: {result['selected_option']}")
    
    def start_monitoring(self):
        """Start monitoring and statistics collection"""
        if not self.config['monitoring_enabled']:
            return
        
        logger.info("Starting monitoring...")
        
        # Monitor engine statistics
        def monitor_stats():
            while True:
                try:
                    if self.engine:
                        stats = self.engine.get_stats()
                        logger.info(f"Engine stats: {stats}")
                    time.sleep(60)  # Log every minute
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(60)
        
        import threading
        monitor_thread = threading.Thread(target=monitor_stats, daemon=True)
        monitor_thread.start()
        logger.info("Monitoring started")
    
    def deploy(self) -> bool:
        """Complete deployment process"""
        logger.info("Starting Bayesian engine deployment...")
        
        # Step 1: Validate environment
        if not self.validate_environment():
            return False
        
        # Step 2: Run tests
        if not self.run_tests():
            return False
        
        # Step 3: Deploy engine
        if not self.deploy_engine():
            return False
        
        # Step 4: Start monitoring
        self.start_monitoring()
        
        logger.info("Bayesian engine deployment completed successfully")
        return True

def main():
    """Main deployment entry point"""
    parser = argparse.ArgumentParser(description='Deploy SOVREN AI Bayesian Engine')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--test-only', action='store_true', help='Run tests only')
    parser.add_argument('--validate-only', action='store_true', help='Validate environment only')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize deployer
    deployer = BayesianEngineDeployer(args.config)
    
    try:
        if args.validate_only:
            # Only validate environment
            success = deployer.validate_environment()
            sys.exit(0 if success else 1)
        
        elif args.test_only:
            # Only run tests
            success = deployer.run_tests()
            sys.exit(0 if success else 1)
        
        else:
            # Full deployment
            success = deployer.deploy()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 