#!/usr/bin/env python3
"""
PandaMonitorBot - Telegram bot for monitoring computer status and other tasks
"""

import asyncio
import signal
from src.utils.logger import setup_logging, get_logger
from src.bot_manager import BotManager


# Setup logging
setup_logging()
logger = get_logger(__name__)


async def main():
    """Main function to start the bot"""
    bot_manager = BotManager()
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    
    def signal_handler(sig, frame):
        signal_name = signal.Signals(sig).name  # перетворює 2 → SIGINT
        logger.info(f"Received signal {signal_name} ({sig}), initiating graceful shutdown...")
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