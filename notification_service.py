import asyncio
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, messaging
from backend.core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.firebase_initialized = False
        self._init_firebase()
    
    def _init_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if settings.FIREBASE_CREDENTIALS_PATH:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
                self.firebase_initialized = True
                logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.warning(f"Firebase initialization failed: {e}")
    
    async def send_push_notification(
        self,
        fcm_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> bool:
        """Send push notification via Firebase Cloud Messaging"""
        if not self.firebase_initialized:
            logger.warning("Firebase not initialized, skipping push notification")
            return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=fcm_token
            )
            
            response = await asyncio.to_thread(messaging.send, message)
            logger.info(f"Push notification sent: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    async def send_new_device_alert(self, user_id: str, device_count: int):
        """Send alert for new devices detected"""
        # TODO: Get user's FCM token from database
        # TODO: Send push notification
        logger.info(f"New device alert for user {user_id}: {device_count} devices")
    
    async def send_security_alert(
        self,
        user_id: str,
        device_name: str,
        severity: str,
        description: str
    ):
        """Send security vulnerability alert"""
        logger.info(f"Security alert for user {user_id}: {device_name} - {severity}")
    
    async def send_email_notification(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """Send email notification"""
        # TODO: Implement email sending using SMTP
        logger.info(f"Email notification: {to_email} - {subject}")
        return True
