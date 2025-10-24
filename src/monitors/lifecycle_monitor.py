"""
Computer Lifecycle Monitor - tracks bot start and stop events
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from telegram.ext import ContextTypes

from config.settings import settings

logger = logging.getLogger(__name__)

class LifecycleMonitor:
    """Monitor bot lifecycle (start/stop) to track computer on/off status"""
    
    def __init__(self, data_file: str = "logs/lifecycle_data.json"):
        self.data_file = data_file
        self.current_startup_time = datetime.now()
        self.is_enabled = True
        self.last_shutdown_time = None
        
        # Ensure logs directory exists
        Path(os.path.dirname(self.data_file)).mkdir(parents=True, exist_ok=True)
        
        # Load previous data
        self._load_data()
        
    def _load_data(self):
        """Load lifecycle data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Get last activity time as previous shutdown
                if 'last_activity' in data:
                    self.last_shutdown_time = datetime.fromisoformat(data['last_activity'])
                    logger.info(f"Loaded last activity: {self.last_shutdown_time}")
            else:
                logger.info("No previous lifecycle data found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading lifecycle data: {e}")
    
    def _save_data(self):
        """Save lifecycle data to file"""
        try:
            data = {
                'last_activity': datetime.now().isoformat(),
                'computer_name': settings.COMPUTER_NAME
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug("Lifecycle data saved")
        except Exception as e:
            logger.error(f"Error saving lifecycle data: {e}")
    
    def _get_session_history_file(self) -> str:
        """Get session history file path"""
        return "logs/session_history.json"
    
    def _load_session_history(self) -> List[Dict]:
        """Load session history from file"""
        try:
            history_file = self._get_session_history_file()
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading session history: {e}")
        return []
    
    def _save_session_history(self, sessions: List[Dict]):
        """Save session history to file"""
        try:
            history_file = self._get_session_history_file()
            Path(os.path.dirname(history_file)).mkdir(parents=True, exist_ok=True)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, indent=2, ensure_ascii=False)
                
            logger.debug("Session history saved")
        except Exception as e:
            logger.error(f"Error saving session history: {e}")
    
    def _add_session_start(self):
        """Add current session start to history"""
        sessions = self._load_session_history()
        
        session = {
            'startup': self.current_startup_time.isoformat(),
            'shutdown': None,
            'computer_name': settings.COMPUTER_NAME
        }
        
        sessions.append(session)
        self._save_session_history(sessions)
    
    def _calculate_today_statistics(self) -> Dict:
        """Calculate activity statistics for today"""
        sessions = self._load_session_history()
        today = datetime.now().date()
        
        total_uptime = timedelta()
        session_count = 0
        first_start = None
        last_activity = None
        
        for session in sessions:
            startup = datetime.fromisoformat(session['startup'])
            
            # Only count sessions that started today
            if startup.date() == today:
                session_count += 1
                
                if first_start is None or startup < first_start:
                    first_start = startup
                
                # Calculate session duration
                if session['shutdown']:
                    shutdown = datetime.fromisoformat(session['shutdown'])
                    duration = shutdown - startup
                else:
                    # Current session - calculate from startup to now
                    duration = datetime.now() - startup
                
                total_uptime += duration
                
                # Track last activity
                end_time = datetime.fromisoformat(session['shutdown']) if session['shutdown'] else datetime.now()
                if last_activity is None or end_time > last_activity:
                    last_activity = end_time
        
        return {
            'session_count': session_count,
            'total_uptime': total_uptime,
            'first_start': first_start,
            'last_activity': last_activity,
            'last_shutdown': self.last_shutdown_time
        }
    
    async def send_startup_notification(self, context: ContextTypes.DEFAULT_TYPE):
        """Send notification when bot starts (computer turned on)"""
        if not self.is_enabled:
            return
            
        try:
            # Add session start to history
            self._add_session_start()
            
            # Save current activity
            self._save_data()
            
            # Calculate statistics
            stats = self._calculate_today_statistics()
            
            message = self._format_startup_message(stats)
            await self._send_to_all_users(context, message)
            logger.info("Startup notification sent to all users")
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
    
    async def update_activity(self, context: ContextTypes.DEFAULT_TYPE):
        """Periodically update activity timestamp"""
        if not self.is_enabled:
            return
            
        try:
            self._save_data()
            logger.debug("Activity timestamp updated")
        except Exception as e:
            logger.error(f"Error updating activity: {e}")
    
    def _format_startup_message(self, stats: Dict) -> str:
        """Format startup notification message with daily statistics"""
        current_time = self.current_startup_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Format uptime
        uptime = stats['total_uptime']
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_str = f"{hours}г {minutes}м" if hours > 0 else f"{minutes}м"
        
        # Format downtime if we have last shutdown
        downtime_str = "Перший запуск сьогодні"
        if self.last_shutdown_time:
            downtime = self.current_startup_time - self.last_shutdown_time
            down_hours, down_remainder = divmod(int(downtime.total_seconds()), 3600)
            down_minutes, _ = divmod(down_remainder, 60)
            
            if down_hours > 24:
                days = down_hours // 24
                downtime_str = f"{days}д {down_hours % 24}г"
            elif down_hours > 0:
                downtime_str = f"{down_hours}г {down_minutes}м"
            else:
                downtime_str = f"{down_minutes}м"
        
        first_start_str = stats['first_start'].strftime('%H:%M:%S') if stats['first_start'] else "N/A"
        
        return f"""
� {settings.COMPUTER_NAME} запущено!

📅 Поточний старт: {current_time}
⏱️ Час простою: {downtime_str}

📊 Статистика за сьогодні:
• Кількість сесій: {stats['session_count']}
• Перший запуск: {first_start_str}
• Загальний час роботи: {uptime_str}

Використовуйте /help для перегляду команд.
"""
    
    async def _send_to_all_users(self, context: ContextTypes.DEFAULT_TYPE, message: str):
        """Send message to all authorized users"""
        for user_id in settings.ALLOWED_USER_IDS:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
                logger.info(f"Message sent to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
    
    def get_info(self) -> dict:
        """Get lifecycle monitor information"""
        stats = self._calculate_today_statistics()
        
        return {
            'startup_time': self.current_startup_time,
            'last_shutdown': self.last_shutdown_time,
            'is_enabled': self.is_enabled,
            'computer_name': settings.COMPUTER_NAME,
            'today_stats': stats
        }
    
    def enable(self):
        """Enable lifecycle monitoring"""
        self.is_enabled = True
        logger.info("Lifecycle monitoring enabled")
    
    def disable(self):
        """Disable lifecycle monitoring"""
        self.is_enabled = False
        logger.info("Lifecycle monitoring disabled")
