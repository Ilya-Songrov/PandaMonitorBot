#!/usr/bin/env python3
"""
PandaMonitorBot - Telegram bot for monitoring computer status and other tasks
"""

import asyncio
import logging
import os
from src.bot_manager import BotManager


# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    bot_manager = BotManager()
    await bot_manager.start()

if __name__ == '__main__':
    asyncio.run(main())