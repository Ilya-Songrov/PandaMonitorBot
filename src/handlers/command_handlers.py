"""
Command handlers for the Telegram bot
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from config.settings import settings
from src.utils.decorators import authorized_only
from src.utils.system_info import get_system_info

logger = logging.getLogger(__name__)

@authorized_only
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = f"""
🐼 Вітаю в PandaMonitorBot! 

Цей бот може виконувати різні задачі моніторингу:
• Моніторинг включення/вимкнення комп'ютера
• Системна інформація
• Інші задачі (в розробці)

Використовуйте /help для перегляду доступних команд.

Комп'ютер: {settings.COMPUTER_NAME}
"""
    await update.message.reply_text(welcome_message)

@authorized_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📋 Доступні команди:

/start - Початкове повідомлення
/help - Показати це повідомлення
/status - Поточний статус системи
/monitor - Запустити моніторинг
/stop_monitor - Зупинити моніторинг
/system_info - Детальна інформація про систему

🔧 Адміністративні команди будуть додані в майбутньому.
"""
    await update.message.reply_text(help_text)

@authorized_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    status_message = f"""
📊 Статус системи:

🖥️ Комп'ютер: {settings.COMPUTER_NAME}
🟢 Статус: Онлайн
⏱️ Інтервал моніторингу: {settings.MONITOR_INTERVAL} сек

Бот працює нормально ✅
"""
    await update.message.reply_text(status_message)

@authorized_only
async def monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /monitor command"""
    # Check if monitoring is already running
    current_jobs = context.job_queue.get_jobs_by_name("computer_monitor")
    
    if current_jobs:
        await update.message.reply_text("🔄 Моніторинг вже запущений!")
        return
    
    # Start monitoring
    from src.monitors.computer_monitor import ComputerMonitor
    monitor = ComputerMonitor()
    
    context.job_queue.run_repeating(
        monitor.check_status,
        interval=settings.MONITOR_INTERVAL,
        first=5,
        name="computer_monitor"
    )
    
    await update.message.reply_text(f"✅ Моніторинг запущений!\nІнтервал: {settings.MONITOR_INTERVAL} секунд")

@authorized_only
async def stop_monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop_monitor command"""
    current_jobs = context.job_queue.get_jobs_by_name("computer_monitor")
    
    if not current_jobs:
        await update.message.reply_text("❌ Моніторинг не запущений!")
        return
    
    for job in current_jobs:
        job.schedule_removal()
    
    await update.message.reply_text("⏹️ Моніторинг зупинений!")

@authorized_only
async def system_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /system_info command"""
    try:
        info = get_system_info()
        message = f"""
🖥️ Системна інформація:

💻 ОС: {info['os']}
🏷️ Ім'я хоста: {info['hostname']}
⚡ CPU: {info['cpu_percent']}%
🧠 RAM: {info['memory_percent']}% ({info['memory_used']}/{info['memory_total']})
💾 Диск: {info['disk_percent']}% ({info['disk_used']}/{info['disk_total']})
🌡️ Температура CPU: {info.get('cpu_temp', 'N/A')}°C
⏰ Uptime: {info['uptime']}
"""
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        await update.message.reply_text("❌ Помилка при отриманні системної інформації")