#!/usr/bin/env python3
"""
SOVREN AI Database Connection Manager
Production-ready PostgreSQL connection handling with pooling and retry logic
"""

import os
import logging
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError, DisconnectionError
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """
    Production-ready database connection manager
    Handles connection pooling, retry logic, and health checks
    """
    
    def __init__(self, database_url: str, max_retries: int = 3, retry_delay: float = 1.0):
        self.database_url = database_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with production settings"""
        try:
            # Parse database URL for connection parameters
            db_params = self._parse_database_url()
            
            # Create engine with production-optimized settings
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=20,  # Maximum number of connections
                max_overflow=30,  # Additional connections beyond pool_size
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,  # Recycle connections every hour
                pool_timeout=30,  # Timeout for getting connection from pool
                echo=False,  # Disable SQL logging in production
                connect_args={
                    'connect_timeout': 10,
                    'application_name': 'sovren_ai',
                    'options': '-c timezone=utc'
                }
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Add connection event listeners
            self._setup_connection_events()
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def _parse_database_url(self) -> Dict[str, Any]:
        """Parse database URL for connection parameters"""
        # Extract components from postgresql://user:pass@host:port/dbname
        url_parts = self.database_url.replace('postgresql://', '').split('@')
        auth_part = url_parts[0]
        host_db_part = url_parts[1]
        
        username, password = auth_part.split(':')
        host_port, database = host_db_part.split('/')
        
        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host = host_port
            port = '5432'
        
        return {
            'host': host,
            'port': int(port),
            'database': database,
            'user': username,
            'password': password
        }
    
    def _setup_connection_events(self):
        """Setup connection event listeners for monitoring"""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set PostgreSQL-specific connection parameters"""
            if hasattr(dbapi_connection, 'set_session'):
                dbapi_connection.set_session(
                    autocommit=False,
                    readonly=False,
                    deferrable=False
                )
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout for monitoring"""
            logger.debug("Database connection checked out")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin for monitoring"""
            logger.debug("Database connection checked in")
    
    def get_session(self) -> Session:
        """Get a database session with retry logic"""
        session = None
        for attempt in range(self.max_retries):
            try:
                session = self.SessionLocal()
                # Test the connection
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
                return session
            except (OperationalError, DisconnectionError) as e:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if session:
                    session.close()
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error("All database connection attempts failed")
                    raise
            except Exception as e:
                logger.error(f"Unexpected database error: {e}")
                if session:
                    session.close()
                raise
        
        # This should never be reached, but satisfies type checker
        raise RuntimeError("Failed to create database session")
    
    @contextmanager
    def get_session_context(self):
        """Context manager for database sessions with automatic cleanup"""
        session = None
        try:
            session = self.get_session()
            yield session
            session.commit()
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            if session:
                session.close()
    
    def health_check(self) -> bool:
        """Perform database health check"""
        try:
            with self.get_session_context() as session:
                from sqlalchemy import text
                result = session.execute(text("SELECT 1")).fetchone()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        try:
            db_params = self._parse_database_url()
            pool = self.engine.pool
            return {
                'host': db_params['host'],
                'port': db_params['port'],
                'database': db_params['database'],
                'user': db_params['user'],
                'pool_size': getattr(pool, 'size', lambda: 0)(),
                'checked_in': getattr(pool, 'checkedin', lambda: 0)(),
                'checked_out': getattr(pool, 'checkedout', lambda: 0)(),
                'overflow': getattr(pool, 'overflow', lambda: 0)(),
                'invalid': getattr(pool, 'invalid', lambda: 0)()
            }
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {}
    
    def close(self):
        """Close all database connections"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

class DatabaseManager:
    """
    High-level database manager for Sovren AI
    Provides easy access to database operations
    """
    
    def __init__(self, database_url: str):
        self.connection_manager = DatabaseConnectionManager(database_url)
        self._setup_database()
    
    def _setup_database(self):
        """Setup database tables and initial data"""
        try:
            from .models import Base, init_database
            init_database(self.connection_manager.database_url)
            logger.info("Database setup completed")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a raw SQL query"""
        with self.connection_manager.get_session_context() as session:
            from sqlalchemy import text
            result = session.execute(text(query), params or {})
            return result.fetchall()
    
    def execute_transaction(self, operations: list) -> bool:
        """Execute multiple operations in a transaction"""
        with self.connection_manager.get_session_context() as session:
            try:
                for operation in operations:
                    if callable(operation):
                        operation(session)
                    else:
                        session.execute(operation)
                return True
            except Exception as e:
                logger.error(f"Transaction failed: {e}")
                return False
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        health_status = {
            'database_connected': self.connection_manager.health_check(),
            'connection_info': self.connection_manager.get_connection_info(),
            'timestamp': time.time()
        }
        
        # Additional health checks
        try:
            with self.connection_manager.get_session_context() as session:
                # Check table counts
                from .models import Company, UserSession
                company_count = session.query(Company).count()
                session_count = session.query(UserSession).count()
                
                health_status.update({
                    'company_count': company_count,
                    'session_count': session_count,
                    'all_systems_operational': True
                })
        except Exception as e:
            health_status.update({
                'all_systems_operational': False,
                'error': str(e)
            })
        
        return health_status
    
    def close(self):
        """Close database manager"""
        self.connection_manager.close()

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

def get_database_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_manager
    
    if _db_manager is None:
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'postgresql://sovren_user:sovren_password@localhost:5432/sovren_ai')
        
        _db_manager = DatabaseManager(database_url)
    
    return _db_manager

def close_database_manager():
    """Close the global database manager"""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None 