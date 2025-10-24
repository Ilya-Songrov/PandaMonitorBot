"""
Computer monitoring functionality
"""

import asyncio
import logging
import platform
import psutil
from datetime import datetime
from telegram.ext import ContextTypes

from config.settings import settings

logger = logging.getLogger(__name__)

class ComputerMonitor:
    """Monitor computer status and send notifications"""
    
    def __init__(self):
        self.last_status = None
        self.startup_time = datetime.now()
        self.is_monitoring = False
        
    async def check_status(self, context: ContextTypes.DEFAULT_TYPE):
        """Check computer status and send notifications if changed"""
        try:
            current_status = self._get_current_status()
            
            # Check if status changed
            if self.last_status is None:
                # First check - computer is online
                await self._send_startup_notification(context)
                self.is_monitoring = True
            elif self.last_status != current_status:
                # Status changed
                await self._send_status_change_notification(context, current_status)
            
            self.last_status = current_status
            
        except Exception as e:
            logger.error(f"Error checking computer status: {e}")
    
    def _get_current_status(self) -> dict:
        """Get current computer status"""
        try:
            return {
                'online': True,
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': datetime.now(),
                'uptime': self._get_uptime()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'online': False,
                'timestamp': datetime.now(),
                'error': str(e)
            }
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}д {hours}г {minutes}м"
            elif hours > 0:
                return f"{hours}г {minutes}м"
            else:
                return f"{minutes}м"
        except Exception:
            return "Невідомо"
    
    async def _send_startup_notification(self, context: ContextTypes.DEFAULT_TYPE):
        """Send computer startup notification"""
        message = f"""
🟢 Комп'ютер {settings.COMPUTER_NAME} онлайн!

📅 Час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 Моніторинг запущений
"""
        await self._send_to_all_users(context, message)
    
    async def _send_status_change_notification(self, context: ContextTypes.DEFAULT_TYPE, status: dict):
        """Send status change notification"""
        if status.get('online'):
            message = f"""
🟢 {settings.COMPUTER_NAME} знову онлайн!

📅 Час: {status['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
💻 CPU: {status.get('cpu_percent', 'N/A')}%
🧠 RAM: {status.get('memory_percent', 'N/A')}%
⏰ Uptime: {status.get('uptime', 'N/A')}
"""
        else:
            message = f"""
🔴 {settings.COMPUTER_NAME} офлайн!

📅 Час: {status['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
❌ Помилка: {status.get('error', 'Невідома')}
"""
        
        await self._send_to_all_users(context, message)
    
    async def _send_to_all_users(self, context: ContextTypes.DEFAULT_TYPE, message: str):
        """Send message to all authorized users"""
        for user_id in settings.ALLOWED_USER_IDS:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
    
    def get_monitor_info(self) -> dict:
        """Get monitoring information"""
        return {
            'is_monitoring': self.is_monitoring,
            'startup_time': self.startup_time,
            'last_check': self.last_status.get('timestamp') if self.last_status else None,
            'computer_name': settings.COMPUTER_NAME
        }