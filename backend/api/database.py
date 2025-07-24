#!/usr/bin/env python3
"""
SOVREN Billing System - Database Persistence
PostgreSQL database layer for audit trails and data persistence
"""

import json
import time
from typing import Dict, List, Any, Optional
from decimal import Decimal
from contextlib import asynccontextmanager
import logging

# Conditional import for asyncpg
asyncpg = None
ASYNCPG_AVAILABLE = False

try:
    import asyncpg  # type: ignore
    ASYNCPG_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger('Database')

class DatabaseManager:
    """PostgreSQL database manager for billing system"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[Any] = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        if not ASYNCPG_AVAILABLE:
            raise RuntimeError("asyncpg is not available. Install with: pip install asyncpg")
        
        if asyncpg is None:
            raise RuntimeError("asyncpg module not available")
        
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=5,
                max_size=20,
                command_timeout=30,
                server_settings={
                    'application_name': 'sovren_billing'
                }
            )
            logger.info("Database connection pool initialized")
            
            # Create tables if they don't exist
            await self._create_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables if they don't exist"""
        async with self.get_connection() as conn:
            # Customers table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id VARCHAR(50) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    metadata JSONB,
                    status VARCHAR(20) DEFAULT 'active'
                )
            """)
            
            # Subscriptions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id VARCHAR(50) PRIMARY KEY,
                    customer_id VARCHAR(50) REFERENCES customers(id),
                    plan_id VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP,
                    billing_period VARCHAR(20) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    next_billing_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    metadata JSONB
                )
            """)
            
            # Invoices table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id VARCHAR(50) PRIMARY KEY,
                    customer_id VARCHAR(50) REFERENCES customers(id),
                    subscription_id VARCHAR(50) REFERENCES subscriptions(id),
                    amount DECIMAL(10,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    due_date TIMESTAMP NOT NULL,
                    paid_date TIMESTAMP,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    line_items JSONB,
                    metadata JSONB
                )
            """)
            
            # Audit trail table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
                    operation VARCHAR(50) NOT NULL,
                    entity_type VARCHAR(50) NOT NULL,
                    entity_id VARCHAR(50) NOT NULL,
                    user_id VARCHAR(50),
                    changes JSONB,
                    ip_address INET,
                    user_agent TEXT
                )
            """)
            
            # Usage tracking table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_tracking (
                    id SERIAL PRIMARY KEY,
                    subscription_id VARCHAR(50) REFERENCES subscriptions(id),
                    usage_type VARCHAR(50) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    metadata JSONB
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
                CREATE INDEX IF NOT EXISTS idx_subscriptions_customer ON subscriptions(customer_id);
                CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
                CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id);
                CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
                CREATE INDEX IF NOT EXISTS idx_audit_trail_entity ON audit_trail(entity_type, entity_id);
                CREATE INDEX IF NOT EXISTS idx_audit_trail_timestamp ON audit_trail(timestamp);
                CREATE INDEX IF NOT EXISTS idx_usage_subscription ON usage_tracking(subscription_id);
                CREATE INDEX IF NOT EXISTS idx_usage_type ON usage_tracking(usage_type);
            """)
            
            logger.info("Database tables created/verified")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database not initialized")
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def store_customer(self, customer_data: Dict[str, Any]) -> bool:
        """Store customer in database"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO customers (id, email, name, company, created_at, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                name = EXCLUDED.name,
                company = EXCLUDED.company,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
            """, 
                customer_data['id'],
                customer_data['email'],
                customer_data['name'],
                customer_data.get('company'),
                customer_data['created_at'],
                json.dumps(customer_data.get('metadata', {}))
            )
            return True
    
    async def store_subscription(self, subscription_data: Dict[str, Any]) -> bool:
        """Store subscription in database"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO subscriptions (
                    id, customer_id, plan_id, status, start_date, end_date,
                    billing_period, price, next_billing_date, metadata
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                end_date = EXCLUDED.end_date,
                next_billing_date = EXCLUDED.next_billing_date,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
            """,
                subscription_data['id'],
                subscription_data['customer_id'],
                subscription_data['plan_id'],
                subscription_data['status'],
                subscription_data['start_date'],
                subscription_data.get('end_date'),
                subscription_data['billing_period'],
                float(subscription_data['price']),
                subscription_data['next_billing_date'],
                json.dumps(subscription_data.get('metadata', {}))
            )
            return True
    
    async def store_invoice(self, invoice_data: Dict[str, Any]) -> bool:
        """Store invoice in database"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO invoices (
                    id, customer_id, subscription_id, amount, currency,
                    status, due_date, paid_date, line_items, metadata
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                paid_date = EXCLUDED.paid_date,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
            """,
                invoice_data['id'],
                invoice_data['customer_id'],
                invoice_data.get('subscription_id'),
                float(invoice_data['amount']),
                invoice_data['currency'],
                invoice_data['status'],
                invoice_data['due_date'],
                invoice_data.get('paid_date'),
                json.dumps(invoice_data.get('line_items', [])),
                json.dumps(invoice_data.get('metadata', {}))
            )
            return True
    
    async def record_audit_event(self, operation: str, entity_type: str, 
                               entity_id: str, changes: Dict[str, Any],
                               user_id: Optional[str] = None,
                               ip_address: Optional[str] = None,
                               user_agent: Optional[str] = None) -> bool:
        """Record audit trail event"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO audit_trail (
                    operation, entity_type, entity_id, user_id, changes, ip_address, user_agent
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                operation,
                entity_type,
                entity_id,
                user_id,
                json.dumps(changes),
                ip_address,
                user_agent
            )
            return True
    
    async def record_usage(self, subscription_id: str, usage_type: str,
                         amount: float, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record usage tracking"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO usage_tracking (subscription_id, usage_type, amount, metadata)
                VALUES ($1, $2, $3, $4)
            """,
                subscription_id,
                usage_type,
                amount,
                json.dumps(metadata or {})
            )
            return True
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM customers WHERE id = $1
            """, customer_id)
            
            if row:
                return dict(row)
            return None
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription by ID"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM subscriptions WHERE id = $1
            """, subscription_id)
            
            if row:
                return dict(row)
            return None
    
    async def get_customer_subscriptions(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for a customer"""
        async with self.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM subscriptions WHERE customer_id = $1 ORDER BY created_at DESC
            """, customer_id)
            
            return [dict(row) for row in rows]
    
    async def get_audit_trail(self, entity_type: str, entity_id: str,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail for an entity"""
        async with self.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM audit_trail 
                WHERE entity_type = $1 AND entity_id = $2 
                ORDER BY timestamp DESC 
                LIMIT $3
            """, entity_type, entity_id, limit)
            
            return [dict(row) for row in rows]
    
    async def get_usage_summary(self, subscription_id: str) -> Dict[str, float]:
        """Get usage summary for a subscription"""
        async with self.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT usage_type, SUM(amount) as total
                FROM usage_tracking 
                WHERE subscription_id = $1 
                GROUP BY usage_type
            """, subscription_id)
            
            return {row['usage_type']: float(row['total']) for row in rows}
    
    async def get_billing_metrics(self) -> Dict[str, Any]:
        """Get billing metrics from database"""
        async with self.get_connection() as conn:
            # Customer metrics
            customer_count = await conn.fetchval("SELECT COUNT(*) FROM customers WHERE status = 'active'")
            
            # Subscription metrics
            subscription_count = await conn.fetchval("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
            
            # Revenue metrics
            mrr = await conn.fetchval("""
                SELECT COALESCE(SUM(price), 0) 
                FROM subscriptions 
                WHERE status = 'active' AND billing_period = 'monthly'
            """)
            
            arr = await conn.fetchval("""
                SELECT COALESCE(SUM(price), 0) 
                FROM subscriptions 
                WHERE status = 'active' AND billing_period = 'yearly'
            """)
            
            # Payment metrics
            total_payments = await conn.fetchval("SELECT COUNT(*) FROM invoices WHERE status = 'success'")
            total_revenue = await conn.fetchval("SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE status = 'success'")
            
            return {
                'customers': {
                    'active': customer_count
                },
                'subscriptions': {
                    'active': subscription_count
                },
                'revenue': {
                    'mrr': float(mrr or 0),
                    'arr': float(arr or 0),
                    'total_payments': total_payments,
                    'total_revenue': float(total_revenue or 0)
                }
            }
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

# Global database manager instance
database_manager: Optional[DatabaseManager] = None

async def initialize_database(connection_string: str) -> DatabaseManager:
    """Initialize global database manager"""
    global database_manager
    database_manager = DatabaseManager(connection_string)
    await database_manager.initialize()
    return database_manager

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    if database_manager is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    return database_manager 