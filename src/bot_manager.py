"""
Bot Manager - Main bot management class
"""

import json
import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config.settings import settings
from src.handlers import command_handlers
from src.monitors.computer_monitor import ComputerMonitor
from src.monitors.lifecycle_monitor import LifecycleMonitor

logger = logging.getLogger(__name__)

class BotManager:
    """Main bot manager class"""
    
    def __init__(self):
        self.application = None
        self.computer_monitor = ComputerMonitor()
        self.lifecycle_monitor = LifecycleMonitor()
        
    async def start(self, stop_event):
        """Start the bot"""
        if not settings.validate():
            logger.error("Invalid configuration. Please check your settings.")
            return
            
        # Create application
        self.application = Application.builder().token(settings.BOT_TOKEN).build()
        
        # Add handlers
        self._add_handlers()
        
        # Don't start monitors automatically - user should use /monitor command
        # await self._start_monitors()
        
        # Initialize and start the bot
        logger.info("Starting PandaMonitorBot...")
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            
            # Store startup time in bot_data
            self.application.bot_data['startup_time'] = self.lifecycle_monitor.current_startup_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Send startup notification
            await self.lifecycle_monitor.send_startup_notification(self.application)
            
            # Start lifecycle activity tracker (periodic updates)
            job_queue = self.application.job_queue
            if job_queue:
                job_queue.run_repeating(
                    self.lifecycle_monitor.update_activity,
                    interval=settings.MONITOR_INTERVAL,
                    first=settings.MONITOR_INTERVAL,
                    name="lifecycle_activity_tracker"
                )
                logger.info("Lifecycle activity tracker started")
            
            # Keep the bot running until stop_event is set
            logger.info("Bot is running. Press Ctrl+C to stop.")
            await stop_event.wait()
            
        except Exception as e:
            logger.error(f"Error during bot operation: {e}", exc_info=True)
        finally:
            logger.info("Stopping PandaMonitorBot...")
            try:
                if self.application.updater.running:
                    await self.application.updater.stop()
                if self.application.running:
                    await self.application.stop()
                await self.application.shutdown()
                logger.info("Bot shutdown complete")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}", exc_info=True)
        
    def _add_handlers(self):
        """Add command handlers"""
        handlers = [
            CommandHandler("start", command_handlers.start_command),
            CommandHandler("help", command_handlers.help_command),
            CommandHandler("status", command_handlers.status_command),
            CommandHandler("monitor", command_handlers.monitor_command),
            CommandHandler("stop_monitor", command_handlers.stop_monitor_command),
            CommandHandler("system_info", command_handlers.system_info_command),
            CommandHandler("lifecycle_status", command_handlers.lifecycle_status_command),
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