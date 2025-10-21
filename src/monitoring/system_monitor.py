"""
🌌 SarlakBot v3.1.0 - System Monitoring
Advanced monitoring and alerting system
"""

import asyncio
import time
import psutil
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SystemMetrics:
    """System metrics data class"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    bot_memory_mb: float
    bot_cpu_percent: float
    active_connections: int
    error_count: int
    warning_count: int


class SystemMonitor:
    """
    🌌 System Monitor
    Advanced monitoring and alerting system
    """
    
    def __init__(self):
        self.logger = logger
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 100
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0,
            "error_count": 50,
            "warning_count": 100
        }
        self.alerts_sent = set()
        self.monitoring_active = False
        
    async def start_monitoring(self, interval: int = 60) -> None:
        """Start system monitoring"""
        try:
            self.monitoring_active = True
            self.logger.info("🔍 System monitoring started")
            
            while self.monitoring_active:
                try:
                    await self._collect_metrics()
                    await self._check_alerts()
                    await asyncio.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(interval)
                    
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    async def stop_monitoring(self) -> None:
        """Stop system monitoring"""
        self.monitoring_active = False
        self.logger.info("🛑 System monitoring stopped")
    
    async def _collect_metrics(self) -> None:
        """Collect system metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get bot process metrics
            bot_memory_mb = 0
            bot_cpu_percent = 0
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if proc.info['name'] == 'python' and 'main.py' in ' '.join(proc.info['cmdline'] or []):
                        bot_proc = psutil.Process(proc.info['pid'])
                        bot_memory_mb = bot_proc.memory_info().rss / 1024 / 1024
                        bot_cpu_percent = bot_proc.cpu_percent()
                        break
            except Exception as e:
                self.logger.warning(f"Could not get bot process metrics: {e}")
            
            # Get network connections
            active_connections = len(psutil.net_connections())
            
            # Get error counts from logs (simplified)
            error_count = 0
            warning_count = 0
            try:
                # This would be implemented to read from actual log files
                # For now, we'll use a placeholder
                error_count = 0
                warning_count = 0
            except Exception as e:
                self.logger.warning(f"Could not get log metrics: {e}")
            
            # Create metrics object
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / 1024 / 1024 / 1024,
                bot_memory_mb=bot_memory_mb,
                bot_cpu_percent=bot_cpu_percent,
                active_connections=active_connections,
                error_count=error_count,
                warning_count=warning_count
            )
            
            # Add to history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)
            
            self.logger.debug(f"Metrics collected: CPU {cpu_percent}%, Memory {memory.percent}%")
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
    
    async def _check_alerts(self) -> None:
        """Check for alert conditions"""
        try:
            if not self.metrics_history:
                return
            
            latest = self.metrics_history[-1]
            alerts = []
            
            # Check CPU usage
            if latest.cpu_percent > self.alert_thresholds["cpu_percent"]:
                alerts.append(f"🚨 CPU usage high: {latest.cpu_percent:.1f}%")
            
            # Check memory usage
            if latest.memory_percent > self.alert_thresholds["memory_percent"]:
                alerts.append(f"🚨 Memory usage high: {latest.memory_percent:.1f}%")
            
            # Check disk usage
            if latest.disk_usage_percent > self.alert_thresholds["disk_usage_percent"]:
                alerts.append(f"🚨 Disk usage high: {latest.disk_usage_percent:.1f}%")
            
            # Check error count
            if latest.error_count > self.alert_thresholds["error_count"]:
                alerts.append(f"🚨 High error count: {latest.error_count}")
            
            # Check warning count
            if latest.warning_count > self.alert_thresholds["warning_count"]:
                alerts.append(f"⚠️ High warning count: {latest.warning_count}")
            
            # Send alerts
            for alert in alerts:
                alert_key = f"{alert}_{latest.timestamp.strftime('%Y%m%d%H')}"
                if alert_key not in self.alerts_sent:
                    await self._send_alert(alert)
                    self.alerts_sent.add(alert_key)
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    async def _send_alert(self, message: str) -> None:
        """Send alert message"""
        try:
            # Log the alert
            self.logger.warning(f"ALERT: {message}")
            
            # Here you could implement actual alerting mechanisms:
            # - Send to admin via Telegram
            # - Send email notification
            # - Send to monitoring service
            # - Write to alert log file
            
            # For now, just log it
            self.logger.info(f"Alert sent: {message}")
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_summary(self, hours: int = 24) -> Dict:
        """Get metrics summary for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {"error": "No metrics available"}
            
            # Calculate averages
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics)
            
            # Get peak values
            peak_cpu = max(m.cpu_percent for m in recent_metrics)
            peak_memory = max(m.memory_percent for m in recent_metrics)
            peak_disk = max(m.disk_usage_percent for m in recent_metrics)
            
            return {
                "period_hours": hours,
                "data_points": len(recent_metrics),
                "avg_cpu_percent": round(avg_cpu, 2),
                "avg_memory_percent": round(avg_memory, 2),
                "avg_disk_percent": round(avg_disk, 2),
                "peak_cpu_percent": round(peak_cpu, 2),
                "peak_memory_percent": round(peak_memory, 2),
                "peak_disk_percent": round(peak_disk, 2),
                "latest_bot_memory_mb": round(recent_metrics[-1].bot_memory_mb, 2),
                "latest_bot_cpu_percent": round(recent_metrics[-1].bot_cpu_percent, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting metrics summary: {e}")
            return {"error": str(e)}
    
    def get_health_status(self) -> Dict:
        """Get overall system health status"""
        try:
            current = self.get_current_metrics()
            if not current:
                return {"status": "unknown", "message": "No metrics available"}
            
            # Determine health status
            if (current.cpu_percent > 90 or 
                current.memory_percent > 95 or 
                current.disk_usage_percent > 95):
                status = "critical"
            elif (current.cpu_percent > 80 or 
                  current.memory_percent > 85 or 
                  current.disk_usage_percent > 90):
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "timestamp": current.timestamp.isoformat(),
                "cpu_percent": current.cpu_percent,
                "memory_percent": current.memory_percent,
                "disk_percent": current.disk_usage_percent,
                "bot_memory_mb": current.bot_memory_mb,
                "bot_cpu_percent": current.bot_cpu_percent,
                "active_connections": current.active_connections
            }
            
        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {"status": "error", "message": str(e)}


# Global monitor instance
system_monitor = SystemMonitor()
