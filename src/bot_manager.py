"""
Bot Manager - Main bot management class
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config.settings import settings
from src.handlers import command_handlers
from src.monitors.computer_monitor import ComputerMonitor

logger = logging.getLogger(__name__)

class BotManager:
    """Main bot manager class"""
    
    def __init__(self):
        self.application = None
        self.computer_monitor = ComputerMonitor()
        
    async def start(self):
        """Start the bot"""
        if not settings.validate():
            logger.error("Invalid configuration. Please check your settings.")
            return
            
        # Create application
        self.application = Application.builder().token(settings.BOT_TOKEN).build()
        
        # Add handlers
        self._add_handlers()
        
        # Start monitors
        await self._start_monitors()
        
        # Initialize and start the bot
        logger.info("Starting PandaMonitorBot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Keep the bot running
        try:
            # Run until interrupted
            import asyncio
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopping PandaMonitorBot...")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        
    def _add_handlers(self):
        """Add command handlers"""
        handlers = [
            CommandHandler("start", command_handlers.start_command),
            CommandHandler("help", command_handlers.help_command),
            CommandHandler("status", command_handlers.status_command),
            CommandHandler("monitor", command_handlers.monitor_command),
            CommandHandler("stop_monitor", command_handlers.stop_monitor_command),
            CommandHandler("system_info", command_handlers.system_info_command),
        ]
        
        for handler in handlers:
            self.application.add_handler(handler)
            
        logger.info("Command handlers added")
        
    async def _start_monitors(self):
        """Start monitoring services"""
        # Start computer monitor
        job_queue = self.application.job_queue
        if job_queue:
            job_queue.run_repeating(
                self.computer_monitor.check_status,
                interval=settings.MONITOR_INTERVAL,
                first=10,
                name="computer_monitor"
            )
            logger.info("Monitoring services started")
        else:
            logger.error("Job queue not available")