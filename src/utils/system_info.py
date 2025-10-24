"""
System information utilities
"""

import platform
import psutil
import socket
from datetime import datetime
from typing import Dict, Any

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    try:
        # Basic system info
        info = {
            'hostname': socket.gethostname(),
            'os': f"{platform.system()} {platform.release()}",
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or platform.machine(),
        }
        
        # CPU information
        info['cpu_count'] = psutil.cpu_count()
        info['cpu_percent'] = round(psutil.cpu_percent(interval=1), 1)
        
        # Memory information
        memory = psutil.virtual_memory()
        info['memory_total'] = _bytes_to_gb(memory.total)
        info['memory_used'] = _bytes_to_gb(memory.used)
        info['memory_percent'] = round(memory.percent, 1)
        
        # Disk information
        disk = psutil.disk_usage('/')
        info['disk_total'] = _bytes_to_gb(disk.total)
        info['disk_used'] = _bytes_to_gb(disk.used)
        info['disk_percent'] = round((disk.used / disk.total) * 100, 1)
        
        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        info['uptime'] = _format_uptime(uptime)
        info['boot_time'] = boot_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # CPU temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try to get CPU temperature
                cpu_temps = temps.get('coretemp', temps.get('cpu_thermal', []))
                if cpu_temps:
                    info['cpu_temp'] = round(cpu_temps[0].current, 1)
        except (AttributeError, OSError):
            pass  # Temperature sensors not available
        
        # Network information
        try:
            network_info = psutil.net_io_counters()
            info['bytes_sent'] = _bytes_to_mb(network_info.bytes_sent)
            info['bytes_recv'] = _bytes_to_mb(network_info.bytes_recv)
        except:
            pass
        
        return info
        
    except Exception as e:
        return {'error': str(e)}

def _bytes_to_gb(bytes_value: int) -> str:
    """Convert bytes to GB string"""
    gb = bytes_value / (1024**3)
    return f"{gb:.1f}GB"

def _bytes_to_mb(bytes_value: int) -> str:
    """Convert bytes to MB string"""
    mb = bytes_value / (1024**2)
    return f"{mb:.1f}MB"

def _format_uptime(uptime) -> str:
    """Format uptime timedelta to readable string"""
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}д {hours}г {minutes}м"
    elif hours > 0:
        return f"{hours}г {minutes}м"
    else:
        return f"{minutes}м"

def is_system_online() -> bool:
    """Check if system is responsive"""
    try:
        # Simple check - if we can get CPU percent, system is responsive
        psutil.cpu_percent(interval=0.1)
        return True
    except:
        return False

def get_process_count() -> int:
    """Get number of running processes"""
    try:
        return len(psutil.pids())
    except:
        return 0