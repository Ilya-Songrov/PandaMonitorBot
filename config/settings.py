"""
Configuration settings for PandaMonitorBot
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Bot settings configuration"""
    
    # Deployment settings
    DEPLOY_ROOT_DIR: str = os.getenv('DEPLOY_ROOT_DIR', '.')
    
    # Bot configuration
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    ALLOWED_USER_IDS: List[int] = [
        int(user_id) for user_id in os.getenv('ALLOWED_USER_IDS', '').split(',') 
        if user_id.strip()
    ]
    
    # Monitoring settings
    MONITOR_INTERVAL: int = int(os.getenv('MONITOR_INTERVAL', '60'))  # seconds
    COMPUTER_NAME: str = os.getenv('COMPUTER_NAME', 'MyComputer')
    
    # Database settings (for future use)
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///bot_data.db')
    
    # Logging settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'bot.log')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings"""
        if not cls.BOT_TOKEN:
            return False
        if not cls.ALLOWED_USER_IDS:
            return False
        return True

# Global settings instance
settings = Settings()