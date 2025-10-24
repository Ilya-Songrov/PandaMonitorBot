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
/lifecycle_status - Статус lifecycle монітора

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

@authorized_only
async def lifecycle_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lifecycle_status command"""
    try:
        # Get bot manager's lifecycle monitor if available
        from src.monitors.lifecycle_monitor import LifecycleMonitor
        
        # Create temp monitor to read stats
        monitor = LifecycleMonitor()
        info = monitor.get_info()
        stats = info['today_stats']
        
        # Format uptime
        uptime = stats['total_uptime']
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_str = f"{hours}г {minutes}м" if hours > 0 else f"{minutes}м"
        
        # Format times
        current_start = info['startup_time'].strftime('%H:%M:%S')
        first_start = stats['first_start'].strftime('%H:%M:%S') if stats['first_start'] else "N/A"
        
        # Downtime info
        downtime_info = ""
        if info['last_shutdown']:
            last_shutdown = info['last_shutdown'].strftime('%Y-%m-%d %H:%M:%S')
            downtime_info = f"\n🔴 Останнє вимкнення: {last_shutdown}"
        
        message = f"""
🔄 Lifecycle Monitor статус:

🖥️ Комп'ютер: {info['computer_name']}
🟢 Поточний старт: {current_start}
✅ Моніторинг: Активний{downtime_info}

📊 Статистика за сьогодні ({stats['session_count']} сесій):
• Перший запуск: {first_start}
• Загальний час роботи: {uptime_str}

ℹ️ Інтервал оновлення: {settings.MONITOR_INTERVAL} сек
💾 Дані зберігаються в: logs/lifecycle_data.json
"""
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error getting lifecycle status: {e}", exc_info=True)
        await update.message.reply_text("❌ Помилка при отриманні статусу lifecycle монітора")
