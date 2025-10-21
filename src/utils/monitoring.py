"""
🌌 SarlakBot v3.2.0 - Monitoring System
Comprehensive system monitoring and health checks
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class HealthStatus:
    """Health status container"""

    status: str
    timestamp: datetime
    details: dict[str, Any]
    errors: list


class SystemMonitor:
    """
    🌌 System Monitor
    Comprehensive system monitoring and health checks
    """

    def __init__(self):
        self.logger = logger
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = None
        self.health_history = []

    async def health_check(self) -> HealthStatus:
        """
        Perform comprehensive health check

        Returns:
            Health status
        """
        try:
            start_time = time.time()
            errors = []
            details = {}

            # Check database health
            db_health = await self._check_database_health()
            if db_health["status"] != "healthy":
                errors.append(f"Database: {db_health.get('error', 'Unknown error')}")
            details["database"] = db_health

            # Check system resources
            system_health = await self._check_system_resources()
            if system_health["status"] != "healthy":
                errors.append(f"System: {system_health.get('error', 'Unknown error')}")
            details["system"] = system_health

            # Check bot status
            bot_health = await self._check_bot_status()
            if bot_health["status"] != "healthy":
                errors.append(f"Bot: {bot_health.get('error', 'Unknown error')}")
            details["bot"] = bot_health

            # Calculate overall status
            overall_status = "healthy" if not errors else "unhealthy"

            # Add performance metrics
            details["performance"] = {
                "uptime": str(datetime.now() - self.start_time),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate": (self.error_count / max(self.request_count, 1)) * 100,
                "health_check_duration": time.time() - start_time,
            }

            health_status = HealthStatus(
                status=overall_status, timestamp=datetime.now(), details=details, errors=errors
            )

            # Store health history
            self.health_history.append(health_status)
            if len(self.health_history) > 100:  # Keep last 100 checks
                self.health_history.pop(0)

            self.last_health_check = health_status
            return health_status

        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return HealthStatus(
                status="error", timestamp=datetime.now(), details={}, errors=[str(e)]
            )

    async def _check_database_health(self) -> dict[str, Any]:
        """Check database health"""
        try:
            health = await db_manager.health_check()
            return health
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}

    async def _check_system_resources(self) -> dict[str, Any]:
        """Check system resources"""
        try:
            # This is a simplified version - in production you'd use psutil
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "note": "System resource monitoring not implemented",
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}

    async def _check_bot_status(self) -> dict[str, Any]:
        """Check bot status"""
        try:
            return {
                "status": "healthy",
                "uptime": str(datetime.now() - self.start_time),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}

    def increment_request_count(self):
        """Increment request counter"""
        self.request_count += 1

    def increment_error_count(self):
        """Increment error counter"""
        self.error_count += 1

    def get_metrics(self) -> dict[str, Any]:
        """Get system metrics"""
        try:
            uptime = datetime.now() - self.start_time
            error_rate = (self.error_count / max(self.request_count, 1)) * 100

            return {
                "uptime_seconds": uptime.total_seconds(),
                "uptime_human": str(uptime),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate_percent": error_rate,
                "start_time": self.start_time.isoformat(),
                "last_health_check": (
                    self.last_health_check.timestamp.isoformat() if self.last_health_check else None
                ),
            }
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return {}

    def get_health_history(self, limit: int = 10) -> list:
        """Get health check history"""
        try:
            return [
                {
                    "status": health.status,
                    "timestamp": health.timestamp.isoformat(),
                    "errors": health.errors,
                    "details": health.details,
                }
                for health in self.health_history[-limit:]
            ]
        except Exception as e:
            self.logger.error(f"Error getting health history: {e}")
            return []

    async def get_detailed_status(self) -> dict[str, Any]:
        """Get detailed system status"""
        try:
            health = await self.health_check()
            metrics = self.get_metrics()
            history = self.get_health_history(5)

            return {
                "health": {
                    "status": health.status,
                    "timestamp": health.timestamp.isoformat(),
                    "errors": health.errors,
                    "details": health.details,
                },
                "metrics": metrics,
                "history": history,
                "summary": {
                    "overall_status": health.status,
                    "uptime": metrics.get("uptime_human", "Unknown"),
                    "request_count": metrics.get("request_count", 0),
                    "error_rate": metrics.get("error_rate_percent", 0),
                },
            }
        except Exception as e:
            self.logger.error(f"Error getting detailed status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


# Global system monitor instance
system_monitor = SystemMonitor()
