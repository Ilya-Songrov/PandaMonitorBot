#!/usr/bin/env python3
"""
PandaMonitorBot - Telegram bot for monitoring computer status and other tasks
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from src.bot_manager import BotManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    bot_manager = BotManager(bot_token)
    await bot_manager.start()

if __name__ == '__main__':
    asyncio.run(main())