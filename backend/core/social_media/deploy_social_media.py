#!/usr/bin/env python3
"""
Deployment script for Social Media Intelligence System
Handles installation, configuration, and testing of the PhD-level social media management agent.
"""

import os
import sys
import subprocess
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SocialMediaDeployer:
    """Deployment manager for the Social Media Intelligence System."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.social_media_dir = self.project_root / "core" / "social_media"
        self.requirements_file = self.social_media_dir / "requirements.txt"
        self.main_system_file = self.social_media_dir / "social_media_intelligence_system.py"
        
    def install_dependencies(self) -> bool:
        """Install required dependencies."""
        try:
            logger.info("Installing social media intelligence system dependencies...")
            
            # Install requirements
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Dependency installation failed: {result.stderr}")
                return False
            
            logger.info("Dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def validate_system_files(self) -> bool:
        """Validate that all system files exist and are properly structured."""
        try:
            logger.info("Validating system files...")
            
            required_files = [
                self.main_system_file,
                self.requirements_file
            ]
            
            for file_path in required_files:
                if not file_path.exists():
                    logger.error(f"Required file missing: {file_path}")
                    return False
            
            logger.info("System files validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"File validation failed: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run comprehensive tests for the social media intelligence system."""
        try:
            logger.info("Running social media intelligence system tests...")
            
            # Import and run tests
            sys.path.insert(0, str(self.social_media_dir))
            
            from social_media_intelligence_system import TestSocialMediaIntelligenceSystem
            
            # Run all tests
            TestSocialMediaIntelligenceSystem.run_all_tests()
            
            logger.info("All tests passed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return False
    
    def create_configuration(self) -> bool:
        """Create configuration files and environment setup."""
        try:
            logger.info("Creating configuration files...")
            
            # Create .env template
            env_template = """# Social Media Intelligence System Configuration

# API Keys (replace with actual keys)
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# Security Configuration
ENCRYPTION_KEY=your_encryption_key_here
JWT_SECRET=your_jwt_secret_here

# Database Configuration
DATABASE_URL=sqlite:///social_media_intelligence.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=social_media_intelligence.log

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_HOUR=100
RATE_LIMIT_REQUESTS_PER_DAY=1000

# Content Strategy
DEFAULT_POSTING_FREQUENCY=3
MAX_CONTENT_LENGTH=280
OPTIMAL_POSTING_TIMES=9,12,17,21
"""
            
            env_file = self.social_media_dir / ".env.template"
            with open(env_file, 'w') as f:
                f.write(env_template)
            
            # Create configuration directory
            config_dir = self.social_media_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            # Create platform configurations
            platform_config = {
                "linkedin": {
                    "api_version": "v2",
                    "rate_limit": 100,
                    "content_types": ["text", "image", "video"],
                    "optimal_timing": [9, 12, 17],
                    "engagement_factors": ["professional", "thought_leadership", "industry_insights"]
                },
                "twitter": {
                    "api_version": "v2",
                    "rate_limit": 300,
                    "content_types": ["text", "image", "video"],
                    "optimal_timing": [7, 9, 12, 15, 17, 20],
                    "engagement_factors": ["trending", "conversational", "insightful"]
                },
                "instagram": {
                    "api_version": "v1",
                    "rate_limit": 200,
                    "content_types": ["image", "video", "story", "reel"],
                    "optimal_timing": [9, 12, 15, 18, 21],
                    "engagement_factors": ["visual", "authentic", "engaging"]
                }
            }
            
            import json
            config_file = config_dir / "platform_config.json"
            with open(config_file, 'w') as f:
                json.dump(platform_config, f, indent=2)
            
            logger.info("Configuration files created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Configuration creation failed: {e}")
            return False
    
    def setup_security(self) -> bool:
        """Setup security configurations and encryption."""
        try:
            logger.info("Setting up security configurations...")
            
            # Create security directory
            security_dir = self.social_media_dir / "security"
            security_dir.mkdir(exist_ok=True)
            
            # Generate encryption keys
            import secrets
            encryption_key = secrets.token_hex(32)
            jwt_secret = secrets.token_hex(32)
            
            # Create security config
            security_config = {
                "encryption_key": encryption_key,
                "jwt_secret": jwt_secret,
                "api_key_rotation_days": 30,
                "session_timeout_hours": 24,
                "max_failed_attempts": 5,
                "rate_limiting_enabled": True
            }
            
            import json
            security_file = security_dir / "security_config.json"
            with open(security_file, 'w') as f:
                json.dump(security_config, f, indent=2)
            
            logger.info("Security configurations setup successfully")
            return True
            
        except Exception as e:
            logger.error(f"Security setup failed: {e}")
            return False
    
    def create_database_schema(self) -> bool:
        """Create database schema for the social media intelligence system."""
        try:
            logger.info("Creating database schema...")
            
            # Create database directory
            db_dir = self.social_media_dir / "database"
            db_dir.mkdir(exist_ok=True)
            
            # Create schema file
            schema_sql = """
-- Social Media Intelligence System Database Schema

-- User profiles and configurations
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT PRIMARY KEY,
    profile_data JSON,
    brand_personality JSON,
    audience_segments JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Content calendar and scheduling
CREATE TABLE IF NOT EXISTS content_calendar (
    calendar_id TEXT PRIMARY KEY,
    user_id TEXT,
    platform TEXT,
    content_type TEXT,
    content_data JSON,
    scheduled_time TIMESTAMP,
    published_time TIMESTAMP,
    engagement_metrics JSON,
    status TEXT DEFAULT 'scheduled',
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

-- Performance analytics and metrics
CREATE TABLE IF NOT EXISTS performance_analytics (
    analytics_id TEXT PRIMARY KEY,
    user_id TEXT,
    platform TEXT,
    date DATE,
    engagement_rate REAL,
    reach_count INTEGER,
    impression_count INTEGER,
    click_through_rate REAL,
    audience_growth INTEGER,
    content_performance JSON,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

-- Platform connections and API configurations
CREATE TABLE IF NOT EXISTS platform_connections (
    connection_id TEXT PRIMARY KEY,
    user_id TEXT,
    platform TEXT,
    api_credentials JSON,
    rate_limit_config JSON,
    connection_status TEXT,
    last_sync TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

-- Content performance history
CREATE TABLE IF NOT EXISTS content_performance (
    performance_id TEXT PRIMARY KEY,
    content_id TEXT,
    platform TEXT,
    engagement_score REAL,
    reach_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    share_count INTEGER,
    click_count INTEGER,
    performance_date TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES content_calendar(calendar_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_content_calendar_user_id ON content_calendar(user_id);
CREATE INDEX IF NOT EXISTS idx_content_calendar_scheduled_time ON content_calendar(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_performance_analytics_user_id ON performance_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_analytics_date ON performance_analytics(date);
CREATE INDEX IF NOT EXISTS idx_platform_connections_user_id ON platform_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_content_performance_content_id ON content_performance(content_id);
"""
            
            schema_file = db_dir / "schema.sql"
            with open(schema_file, 'w') as f:
                f.write(schema_sql)
            
            logger.info("Database schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database schema creation failed: {e}")
            return False
    
    def create_deployment_script(self) -> bool:
        """Create deployment and management scripts."""
        try:
            logger.info("Creating deployment scripts...")
            
            # Create main deployment script
            deploy_script = """#!/usr/bin/env python3
\"\"\"
Social Media Intelligence System - Main Deployment Script
\"\"\"

import asyncio
import logging
from social_media_intelligence_system import SocialMediaIntelligenceSystem

async def main():
    # Initialize the system
    system = SocialMediaIntelligenceSystem()
    
    # Example user profile
    user_profile = {
        'user_id': 'example_user',
        'keywords': ['executive', 'leader', 'strategist'],
        'platforms': ['linkedin', 'twitter', 'instagram'],
        'professional_level': 'senior',
        'network_size': 1500,
        'industry': 'technology',
        'content_preferences': ['thought_leadership', 'industry_insights', 'professional_development']
    }
    
    # Initialize system
    success = await system.initialize_system(user_profile['user_id'], user_profile)
    
    if success:
        print("Social Media Intelligence System initialized successfully")
        
        # Execute content strategy
        results = await system.execute_content_strategy(user_profile['user_id'])
        print(f"Content strategy executed: {results}")
        
        # Get performance analytics
        analytics = await system.get_performance_analytics(user_profile['user_id'])
        print(f"Performance analytics: {analytics}")
    else:
        print("System initialization failed")

if __name__ == "__main__":
    asyncio.run(main())
"""
            
            script_file = self.social_media_dir / "run_system.py"
            with open(script_file, 'w') as f:
                f.write(deploy_script)
            
            # Make script executable
            os.chmod(script_file, 0o755)
            
            logger.info("Deployment scripts created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Deployment script creation failed: {e}")
            return False
    
    def run_deployment(self) -> bool:
        """Execute the complete deployment process."""
        try:
            logger.info("Starting Social Media Intelligence System deployment...")
            
            # Step 1: Validate system files
            if not self.validate_system_files():
                logger.error("System file validation failed")
                return False
            
            # Step 2: Install dependencies
            if not self.install_dependencies():
                logger.error("Dependency installation failed")
                return False
            
            # Step 3: Create configuration
            if not self.create_configuration():
                logger.error("Configuration creation failed")
                return False
            
            # Step 4: Setup security
            if not self.setup_security():
                logger.error("Security setup failed")
                return False
            
            # Step 5: Create database schema
            if not self.create_database_schema():
                logger.error("Database schema creation failed")
                return False
            
            # Step 6: Create deployment scripts
            if not self.create_deployment_script():
                logger.error("Deployment script creation failed")
                return False
            
            # Step 7: Run tests
            if not self.run_tests():
                logger.error("Test execution failed")
                return False
            
            logger.info("Social Media Intelligence System deployment completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False


def main():
    """Main deployment function."""
    deployer = SocialMediaDeployer()
    
    print("=" * 60)
    print("Social Media Intelligence System - PhD-Level Deployment")
    print("=" * 60)
    
    success = deployer.run_deployment()
    
    if success:
        print("\n✅ Deployment completed successfully!")
        print("\nNext steps:")
        print("1. Configure your API keys in .env.template")
        print("2. Run: python run_system.py")
        print("3. Monitor logs for system performance")
        print("\nThe system is now ready for production use.")
    else:
        print("\n❌ Deployment failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main() 