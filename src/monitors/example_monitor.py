"""
Example of a custom monitor - Template for adding new monitoring features
"""

import logging
from datetime import datetime
from telegram.ext import ContextTypes

from config.settings import settings

logger = logging.getLogger(__name__)

class ExampleMonitor:
    """
    Example monitor class - Template for creating new monitors
    
    This is a template showing how to create new monitoring functionality.
    Copy this file and modify it for your specific monitoring needs.
    """
    
    def __init__(self):
        self.name = "Example Monitor"
        self.is_active = False
        self.last_check = None
        
    async def check_status(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Main monitoring method - called periodically
        
        This method will be called at regular intervals.
        Implement your monitoring logic here.
        """
        try:
            # Your monitoring logic here
            status = self._get_status()
            
            # Check if something changed or needs notification
            if self._should_notify(status):
                await self._send_notification(context, status)
                
            # Update last check time
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
    
    def _get_status(self) -> dict:
        """
        Get current status - implement your monitoring logic here
        
        Returns:
            dict: Current status information
        """
        # Example: Check some condition
        return {
            'timestamp': datetime.now(),
            'value': 'example_value',
            'is_ok': True
        }
    
    def _should_notify(self, status: dict) -> bool:
        """
        Determine if notification should be sent
        
        Args:
            status: Current status from _get_status()
            
        Returns:
            bool: True if notification should be sent
        """
        # Example logic: notify if status changed or on first check
        if self.last_check is None:
            return True
            
        # Add your notification logic here
        return False
    
    async def _send_notification(self, context: ContextTypes.DEFAULT_TYPE, status: dict):
        """
        Send notification to users
        
        Args:
            context: Telegram context
            status: Status information to include in notification
        """
        message = f"""
🔔 {self.name} Notification

📅 Time: {status['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
📊 Status: {'✅ OK' if status.get('is_ok') else '❌ Issue'}
📈 Value: {status.get('value', 'N/A')}
"""
        
        # Send to all authorized users
        for user_id in settings.ALLOWED_USER_IDS:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {e}")
    
    def get_info(self) -> dict:
        """
        Get monitor information
        
        Returns:
            dict: Monitor information
        """
        return {
            'name': self.name,
            'is_active': self.is_active,
            'last_check': self.last_check
        }

# Example of how to add this monitor to the bot:
"""
1. Import in bot_manager.py:
   from src.monitors.example_monitor import ExampleMonitor

2. Add to _start_monitors method in BotManager:
   self.example_monitor = ExampleMonitor()
   self.application.job_queue.run_repeating(
       self.example_monitor.check_status,
       interval=300,  # 5 minutes
       first=30,
       name="example_monitor"
   )

3. Add commands to control the monitor in command_handlers.py if needed
"""