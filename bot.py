#!/usr/bin/env python3
"""
PandaMonitorBot - Telegram bot for monitoring computer status and other tasks
"""

import asyncio
import logging
import signal
import sys
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
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating graceful shutdown...")
        stop_event.set()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await bot_manager.start(stop_event)
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
    finally:
        logger.info("Bot stopped")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass