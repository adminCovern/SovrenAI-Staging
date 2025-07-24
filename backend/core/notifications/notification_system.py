#!/usr/bin/env python3
"""
SOVREN AI Notification System
Real-time notifications and alerts
Production-ready implementation with enterprise standards
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    """Types of notifications"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    URGENT = "urgent"
    SYSTEM = "system"

class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Notification:
    """Notification model"""
    notification_id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    user_id: str
    timestamp: datetime
    read: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class NotificationSystem:
    """Notification system for real-time alerts"""
    
    def __init__(self):
        self.is_running = False
        self.notifications: Dict[str, Notification] = {}
        self.user_notifications: Dict[str, List[str]] = {}
        self.notification_handlers: Dict[NotificationType, Callable[[Notification], Awaitable[None]]] = {}
        
        # Initialize notification handlers
        self._initialize_handlers()
        
    def _initialize_handlers(self):
        """Initialize notification handlers"""
        self.notification_handlers = {
            NotificationType.INFO: self._handle_info_notification,
            NotificationType.WARNING: self._handle_warning_notification,
            NotificationType.ERROR: self._handle_error_notification,
            NotificationType.SUCCESS: self._handle_success_notification,
            NotificationType.URGENT: self._handle_urgent_notification,
            NotificationType.SYSTEM: self._handle_system_notification
        }
    
    async def start(self):
        """Start the notification system"""
        try:
            self.is_running = True
            logger.info("Notification System started successfully")
            
            # Start background notification tasks
            asyncio.create_task(self._background_notification_loop())
            
        except Exception as e:
            logger.error(f"Failed to start notification system: {e}")
            raise
    
    async def stop(self):
        """Stop the notification system"""
        try:
            self.is_running = False
            logger.info("Notification System stopped")
            
        except Exception as e:
            logger.error(f"Error stopping notification system: {e}")
    
    async def send_notification(self, user_id: str, notification_type: NotificationType,
                              priority: NotificationPriority, title: str, message: str,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send a notification to a user"""
        try:
            notification_id = f"notif_{int(time.time())}_{user_id}"
            
            notification = Notification(
                notification_id=notification_id,
                type=notification_type,
                priority=priority,
                title=title,
                message=message,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Store notification
            self.notifications[notification_id] = notification
            
            # Add to user's notification list
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            self.user_notifications[user_id].append(notification_id)
            
            # Handle notification based on type
            if notification_type in self.notification_handlers:
                await self.notification_handlers[notification_type](notification)
            
            logger.info(f"Notification sent to user {user_id}: {title}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            raise
    
    async def get_user_notifications(self, user_id: str, 
                                   unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user"""
        try:
            if user_id not in self.user_notifications:
                return []
            
            notification_ids = self.user_notifications[user_id]
            notifications = []
            
            for notification_id in notification_ids:
                if notification_id in self.notifications:
                    notification = self.notifications[notification_id]
                    if not unread_only or not notification.read:
                        notifications.append(notification)
            
            # Sort by timestamp (newest first)
            notifications.sort(key=lambda x: x.timestamp, reverse=True)
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            if notification_id in self.notifications:
                self.notifications[notification_id].read = True
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        try:
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                user_id = notification.user_id
                
                # Remove from notifications
                del self.notifications[notification_id]
                
                # Remove from user's notification list
                if user_id in self.user_notifications:
                    if notification_id in self.user_notifications[user_id]:
                        self.user_notifications[user_id].remove(notification_id)
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            return False
    
    async def _handle_info_notification(self, notification: Notification):
        """Handle info notification"""
        logger.info(f"Info notification: {notification.title} - {notification.message}")
        # Could send to email, push notification, etc.
    
    async def _handle_warning_notification(self, notification: Notification):
        """Handle warning notification"""
        logger.warning(f"Warning notification: {notification.title} - {notification.message}")
        # Could send to email, push notification, etc.
    
    async def _handle_error_notification(self, notification: Notification):
        """Handle error notification"""
        logger.error(f"Error notification: {notification.title} - {notification.message}")
        # Could send to email, push notification, etc.
    
    async def _handle_success_notification(self, notification: Notification):
        """Handle success notification"""
        logger.info(f"Success notification: {notification.title} - {notification.message}")
        # Could send to email, push notification, etc.
    
    async def _handle_urgent_notification(self, notification: Notification):
        """Handle urgent notification"""
        logger.critical(f"Urgent notification: {notification.title} - {notification.message}")
        # Could send to email, push notification, etc.
    
    async def _handle_system_notification(self, notification: Notification):
        """Handle system notification"""
        logger.info(f"System notification: {notification.title} - {notification.message}")
        # Could send to email, push notification, etc.
    
    async def _background_notification_loop(self):
        """Background notification loop"""
        while self.is_running:
            try:
                # Process pending notifications
                await self._process_pending_notifications()
                
                # Clean up old notifications
                await self._cleanup_old_notifications()
                
                await asyncio.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in background notification loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _process_pending_notifications(self):
        """Process pending notifications"""
        try:
            # Process high priority notifications first
            for notification in self.notifications.values():
                if notification.priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL]:
                    if not notification.read:
                        # Process urgent notifications
                        await self._process_urgent_notification(notification)
            
        except Exception as e:
            logger.error(f"Error processing pending notifications: {e}")
    
    async def _process_urgent_notification(self, notification: Notification):
        """Process urgent notification"""
        try:
            # Send immediate alert for urgent notifications
            if notification.priority == NotificationPriority.CRITICAL:
                await self._send_immediate_alert(notification)
            
        except Exception as e:
            logger.error(f"Error processing urgent notification: {e}")
    
    async def _send_immediate_alert(self, notification: Notification):
        """Send immediate alert for critical notifications"""
        try:
            # This could send SMS, email, or other immediate alerts
            logger.critical(f"CRITICAL ALERT: {notification.title} - {notification.message}")
            
        except Exception as e:
            logger.error(f"Error sending immediate alert: {e}")
    
    async def _cleanup_old_notifications(self):
        """Clean up old notifications"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            notifications_to_delete = []
            
            for notification_id, notification in self.notifications.items():
                if notification.timestamp < cutoff_time and notification.read:
                    notifications_to_delete.append(notification_id)
            
            for notification_id in notifications_to_delete:
                await self.delete_notification(notification_id)
                
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {e}")

# Global instance
_notification_system = None

def get_notification_system() -> NotificationSystem:
    """Get the global notification system instance"""
    global _notification_system
    if _notification_system is None:
        _notification_system = NotificationSystem()
    return _notification_system

async def start_notification_system():
    """Start the global notification system"""
    notification_system = get_notification_system()
    await notification_system.start()

async def stop_notification_system():
    """Stop the global notification system"""
    global _notification_system
    if _notification_system:
        await _notification_system.stop()
        _notification_system = None 