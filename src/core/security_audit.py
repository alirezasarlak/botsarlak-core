"""
🌌 SarlakBot v3.0 - Security & Audit System
Comprehensive security monitoring and audit logging
"""

import json
import hashlib
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SecurityLevel(Enum):
    """Security levels for audit logs"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ActionType(Enum):
    """Types of actions to audit"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTRATION = "user_registration"
    ADMIN_ACTION = "admin_action"
    ROUTE_ACCESS = "route_access"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SECURITY_VIOLATION = "security_violation"
    SYSTEM_EVENT = "system_event"


@dataclass
class AuditLog:
    """Audit log entry"""
    user_id: Optional[int]
    action: ActionType
    resource: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.INFO
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SecurityAuditor:
    """
    🌌 Security Auditor
    Comprehensive security monitoring and audit logging
    """
    
    def __init__(self):
        self.logger = logger
        self._rate_limit_cache: Dict[str, List[datetime]] = {}
        self._suspicious_activities: Dict[str, int] = {}
    
    async def log_audit_event(self, audit_log: AuditLog) -> bool:
        """
        Log audit event to database
        
        Args:
            audit_log: Audit log entry
            
        Returns:
            Success status
        """
        try:
            # Check rate limiting
            if not await self._check_rate_limit(audit_log.user_id, audit_log.action):
                self.logger.warning(f"Rate limit exceeded for user {audit_log.user_id}")
                return False
            
            # Check for suspicious activity
            await self._check_suspicious_activity(audit_log)
            
            # Log to database
            query = """
                INSERT INTO audit_logs (
                    user_id, action, resource, details, ip_address, 
                    user_agent, security_level, created_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8
                )
            """
            
            await db_manager.execute(
                query,
                audit_log.user_id,
                audit_log.action.value,
                audit_log.resource,
                json.dumps(audit_log.details),
                audit_log.ip_address,
                audit_log.user_agent,
                audit_log.security_level.value,
                audit_log.timestamp
            )
            
            # Log to application logs
            self.logger.info(f"Audit: {audit_log.action.value} by user {audit_log.user_id} on {audit_log.resource}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            return False
    
    async def _check_rate_limit(self, user_id: Optional[int], action: ActionType) -> bool:
        """Check rate limiting for user actions"""
        try:
            if user_id is None:
                return True  # No rate limiting for anonymous actions
            
            key = f"{user_id}_{action.value}"
            now = datetime.now()
            
            # Get recent actions
            if key not in self._rate_limit_cache:
                self._rate_limit_cache[key] = []
            
            # Remove old entries (older than 1 minute)
            self._rate_limit_cache[key] = [
                timestamp for timestamp in self._rate_limit_cache[key]
                if now - timestamp < timedelta(minutes=1)
            ]
            
            # Check rate limits based on action type
            if action == ActionType.USER_LOGIN:
                max_attempts = 5
            elif action == ActionType.ADMIN_ACTION:
                max_attempts = 10
            elif action == ActionType.ROUTE_ACCESS:
                max_attempts = 100
            else:
                max_attempts = 50
            
            if len(self._rate_limit_cache[key]) >= max_attempts:
                return False
            
            # Add current action
            self._rate_limit_cache[key].append(now)
            return True
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    async def _check_suspicious_activity(self, audit_log: AuditLog) -> None:
        """Check for suspicious activity patterns"""
        try:
            if audit_log.user_id is None:
                return
            
            # Check for rapid successive actions
            key = f"suspicious_{audit_log.user_id}"
            now = datetime.now()
            
            if key not in self._suspicious_activities:
                self._suspicious_activities[key] = 0
            
            # Reset counter if last activity was more than 5 minutes ago
            # (This is a simplified check - in production, you'd use a proper cache)
            
            # Increment suspicious activity counter
            self._suspicious_activities[key] += 1
            
            # Alert if suspicious activity detected
            if self._suspicious_activities[key] > 20:  # More than 20 actions in 5 minutes
                await self._alert_suspicious_activity(audit_log)
                self._suspicious_activities[key] = 0  # Reset counter
            
        except Exception as e:
            self.logger.error(f"Suspicious activity check failed: {e}")
    
    async def _alert_suspicious_activity(self, audit_log: AuditLog) -> None:
        """Alert about suspicious activity"""
        try:
            # Log critical security event
            security_log = AuditLog(
                user_id=audit_log.user_id,
                action=ActionType.SECURITY_VIOLATION,
                resource="suspicious_activity",
                details={
                    "reason": "rapid_successive_actions",
                    "count": self._suspicious_activities.get(f"suspicious_{audit_log.user_id}", 0),
                    "original_action": audit_log.action.value,
                    "original_resource": audit_log.resource
                },
                security_level=SecurityLevel.CRITICAL
            )
            
            await self.log_audit_event(security_log)
            
            # Send alert to admin (implement based on your notification system)
            self.logger.critical(f"SUSPICIOUS ACTIVITY: User {audit_log.user_id} showing suspicious behavior")
            
        except Exception as e:
            self.logger.error(f"Failed to alert suspicious activity: {e}")
    
    async def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[ActionType] = None,
        security_level: Optional[SecurityLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with filters
        
        Args:
            user_id: Filter by user ID
            action: Filter by action type
            security_level: Filter by security level
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            
        Returns:
            List of audit log entries
        """
        try:
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            param_count = 0
            
            if user_id is not None:
                param_count += 1
                query += f" AND user_id = ${param_count}"
                params.append(user_id)
            
            if action is not None:
                param_count += 1
                query += f" AND action = ${param_count}"
                params.append(action.value)
            
            if security_level is not None:
                param_count += 1
                query += f" AND security_level = ${param_count}"
                params.append(security_level.value)
            
            if start_date is not None:
                param_count += 1
                query += f" AND created_at >= ${param_count}"
                params.append(start_date)
            
            if end_date is not None:
                param_count += 1
                query += f" AND created_at <= ${param_count}"
                params.append(end_date)
            
            query += f" ORDER BY created_at DESC LIMIT {limit}"
            
            logs = await db_manager.fetch_all(query, *params)
            
            # Parse JSON details
            for log in logs:
                if log.get('details'):
                    try:
                        log['details'] = json.loads(log['details'])
                    except:
                        log['details'] = {}
            
            return logs
            
        except Exception as e:
            self.logger.error(f"Failed to get audit logs: {e}")
            return []
    
    async def get_security_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get security summary for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Security summary
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get total events
            total_events = await db_manager.fetch_value(
                "SELECT COUNT(*) FROM audit_logs WHERE created_at >= $1",
                start_date
            ) or 0
            
            # Get events by security level
            security_levels = await db_manager.fetch_all(
                """
                SELECT security_level, COUNT(*) as count 
                FROM audit_logs 
                WHERE created_at >= $1 
                GROUP BY security_level
                """,
                start_date
            )
            
            # Get events by action type
            action_types = await db_manager.fetch_all(
                """
                SELECT action, COUNT(*) as count 
                FROM audit_logs 
                WHERE created_at >= $1 
                GROUP BY action
                ORDER BY count DESC
                LIMIT 10
                """,
                start_date
            )
            
            # Get top users by activity
            top_users = await db_manager.fetch_all(
                """
                SELECT user_id, COUNT(*) as count 
                FROM audit_logs 
                WHERE created_at >= $1 AND user_id IS NOT NULL
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 10
                """,
                start_date
            )
            
            # Get security violations
            security_violations = await db_manager.fetch_value(
                """
                SELECT COUNT(*) FROM audit_logs 
                WHERE created_at >= $1 AND action = 'security_violation'
                """,
                start_date
            ) or 0
            
            return {
                "period_days": days,
                "total_events": total_events,
                "security_levels": {row['security_level']: row['count'] for row in security_levels},
                "action_types": {row['action']: row['count'] for row in action_types},
                "top_users": {row['user_id']: row['count'] for row in top_users},
                "security_violations": security_violations,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get security summary: {e}")
            return {}
    
    async def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """
        Clean up old audit logs
        
        Args:
            days_to_keep: Number of days to keep logs
            
        Returns:
            Number of deleted logs
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Get count before deletion
            count = await db_manager.fetch_value(
                "SELECT COUNT(*) FROM audit_logs WHERE created_at < $1",
                cutoff_date
            ) or 0
            
            # Delete old logs
            await db_manager.execute(
                "DELETE FROM audit_logs WHERE created_at < $1",
                cutoff_date
            )
            
            self.logger.info(f"Cleaned up {count} old audit logs")
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")
            return 0
    
    def generate_audit_token(self, user_id: int, action: str) -> str:
        """
        Generate audit token for tracking
        
        Args:
            user_id: User ID
            action: Action being performed
            
        Returns:
            Audit token
        """
        try:
            # Create token data
            token_data = {
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "nonce": secrets.token_hex(16)
            }
            
            # Create hash
            token_string = json.dumps(token_data, sort_keys=True)
            token_hash = hashlib.sha256(token_string.encode()).hexdigest()
            
            return token_hash
            
        except Exception as e:
            self.logger.error(f"Failed to generate audit token: {e}")
            return ""
    
    async def validate_audit_token(self, token: str, user_id: int, action: str) -> bool:
        """
        Validate audit token
        
        Args:
            token: Token to validate
            user_id: User ID
            action: Action being performed
            
        Returns:
            True if valid
        """
        try:
            # This is a simplified validation
            # In production, you'd store tokens with expiration times
            
            # For now, just check if token is not empty
            return len(token) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to validate audit token: {e}")
            return False


# Global security auditor instance
security_auditor = SecurityAuditor()



