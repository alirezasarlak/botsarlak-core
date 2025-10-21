"""
🌌 SarlakBot v3.1.0 - Anti-Fraud Service
Advanced anti-cheating and fraud detection system
"""

import asyncio
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class FraudRiskLevel(Enum):
    """Fraud risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FraudDetectionResult:
    """Fraud detection result"""
    is_fraud: bool
    risk_level: FraudRiskLevel
    reasons: List[str]
    confidence: float
    actions_taken: List[str]
    metadata: Dict[str, Any]


@dataclass
class StudySessionValidation:
    """Study session validation data"""
    user_id: int
    session_start: datetime
    session_end: datetime
    duration_minutes: int
    questions_answered: int
    correct_answers: int
    device_fingerprint: str
    ip_address: str
    user_agent: str


class AntiFraudService:
    """
    🌌 Anti-Fraud Service
    Advanced anti-cheating and fraud detection system
    """
    
    def __init__(self):
        self.logger = logger
        self.fraud_thresholds = {
            'max_daily_minutes': 480,  # 8 hours
            'max_session_minutes': 180,  # 3 hours
            'min_session_minutes': 5,  # 5 minutes minimum
            'max_questions_per_minute': 10,
            'max_accuracy_threshold': 95,  # Suspicious if too high
            'min_accuracy_threshold': 10,  # Suspicious if too low
            'max_sessions_per_day': 20,
            'suspicious_pattern_threshold': 3
        }
    
    async def validate_study_session(
        self, 
        user_id: int, 
        duration_minutes: int,
        questions_answered: int = 0,
        correct_answers: int = 0,
        device_info: Dict[str, str] = None
    ) -> FraudDetectionResult:
        """Validate a study session for fraud"""
        try:
            if device_info is None:
                device_info = {}
            
            # Initialize result
            reasons = []
            actions_taken = []
            metadata = {
                'user_id': user_id,
                'duration_minutes': duration_minutes,
                'questions_answered': questions_answered,
                'correct_answers': correct_answers,
                'timestamp': datetime.now()
            }
            
            # 1. Basic validation checks
            basic_checks = await self._perform_basic_checks(
                user_id, duration_minutes, questions_answered, correct_answers
            )
            reasons.extend(basic_checks['reasons'])
            actions_taken.extend(basic_checks['actions'])
            
            # 2. Pattern analysis
            pattern_analysis = await self._analyze_user_patterns(user_id)
            reasons.extend(pattern_analysis['reasons'])
            actions_taken.extend(pattern_analysis['actions'])
            
            # 3. Device and location validation
            device_validation = await self._validate_device_consistency(
                user_id, device_info
            )
            reasons.extend(device_validation['reasons'])
            actions_taken.extend(device_validation['actions'])
            
            # 4. Time-based analysis
            time_analysis = await self._analyze_time_patterns(user_id)
            reasons.extend(time_analysis['reasons'])
            actions_taken.extend(time_analysis['actions'])
            
            # 5. Performance analysis
            performance_analysis = await self._analyze_performance_patterns(
                user_id, questions_answered, correct_answers
            )
            reasons.extend(performance_analysis['reasons'])
            actions_taken.extend(performance_analysis['actions'])
            
            # 6. Determine risk level and fraud status
            risk_level, is_fraud, confidence = self._calculate_risk_level(reasons)
            
            result = FraudDetectionResult(
                is_fraud=is_fraud,
                risk_level=risk_level,
                reasons=reasons,
                confidence=confidence,
                actions_taken=actions_taken,
                metadata=metadata
            )
            
            # 7. Log fraud detection result
            await self._log_fraud_detection(result)
            
            # 8. Take action if fraud detected
            if is_fraud:
                await self._take_fraud_action(user_id, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating study session: {e}")
            # Return safe default
            return FraudDetectionResult(
                is_fraud=False,
                risk_level=FraudRiskLevel.LOW,
                reasons=[],
                confidence=0.0,
                actions_taken=[],
                metadata={'error': str(e)}
            )
    
    async def _perform_basic_checks(
        self, 
        user_id: int, 
        duration_minutes: int,
        questions_answered: int,
        correct_answers: int
    ) -> Dict[str, Any]:
        """Perform basic validation checks"""
        reasons = []
        actions = []
        
        # Check duration limits
        if duration_minutes > self.fraud_thresholds['max_session_minutes']:
            reasons.append(f"Session duration too long: {duration_minutes} minutes")
            actions.append("FLAG_SESSION_DURATION")
        
        if duration_minutes < self.fraud_thresholds['min_session_minutes']:
            reasons.append(f"Session duration too short: {duration_minutes} minutes")
            actions.append("FLAG_SHORT_SESSION")
        
        # Check daily limits
        daily_stats = await self._get_daily_stats(user_id)
        if daily_stats['total_minutes'] + duration_minutes > self.fraud_thresholds['max_daily_minutes']:
            reasons.append(f"Daily study time limit exceeded")
            actions.append("FLAG_DAILY_LIMIT")
        
        if daily_stats['session_count'] >= self.fraud_thresholds['max_sessions_per_day']:
            reasons.append(f"Too many sessions today: {daily_stats['session_count']}")
            actions.append("FLAG_SESSION_COUNT")
        
        # Check question answering speed
        if duration_minutes > 0 and questions_answered > 0:
            questions_per_minute = questions_answered / duration_minutes
            if questions_per_minute > self.fraud_thresholds['max_questions_per_minute']:
                reasons.append(f"Answering speed too high: {questions_per_minute:.1f} questions/minute")
                actions.append("FLAG_ANSWERING_SPEED")
        
        # Check accuracy
        if questions_answered > 0:
            accuracy = (correct_answers / questions_answered) * 100
            if accuracy > self.fraud_thresholds['max_accuracy_threshold']:
                reasons.append(f"Suspiciously high accuracy: {accuracy:.1f}%")
                actions.append("FLAG_HIGH_ACCURACY")
            elif accuracy < self.fraud_thresholds['min_accuracy_threshold']:
                reasons.append(f"Suspiciously low accuracy: {accuracy:.1f}%")
                actions.append("FLAG_LOW_ACCURACY")
        
        return {'reasons': reasons, 'actions': actions}
    
    async def _analyze_user_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user study patterns for anomalies"""
        reasons = []
        actions = []
        
        try:
            # Get user's study history
            async with db_manager.get_connection() as conn:
                # Get last 30 days of study data
                history = await conn.fetch(
                    """
                    SELECT report_date, study_minutes, tests_count, correct_answers, total_questions
                    FROM study_reports 
                    WHERE user_id = $1 AND report_date >= CURRENT_DATE - INTERVAL '30 days'
                    ORDER BY report_date DESC
                    """,
                    user_id
                )
                
                if len(history) < 3:
                    return {'reasons': reasons, 'actions': actions}
                
                # Analyze consistency patterns
                daily_minutes = [row['study_minutes'] for row in history]
                avg_daily = sum(daily_minutes) / len(daily_minutes)
                
                # Check for sudden spikes
                recent_avg = sum(daily_minutes[:3]) / 3
                if recent_avg > avg_daily * 2:
                    reasons.append("Sudden increase in study time detected")
                    actions.append("FLAG_STUDY_SPIKE")
                
                # Check for perfect consistency (suspicious)
                if len(set(daily_minutes)) == 1 and daily_minutes[0] > 0:
                    reasons.append("Perfectly consistent study times (suspicious)")
                    actions.append("FLAG_PERFECT_CONSISTENCY")
                
                # Analyze accuracy patterns
                accuracies = []
                for row in history:
                    if row['total_questions'] > 0:
                        acc = (row['correct_answers'] / row['total_questions']) * 100
                        accuracies.append(acc)
                
                if len(accuracies) > 5:
                    avg_accuracy = sum(accuracies) / len(accuracies)
                    if avg_accuracy > 95:
                        reasons.append("Consistently high accuracy (suspicious)")
                        actions.append("FLAG_CONSISTENT_HIGH_ACCURACY")
                
        except Exception as e:
            self.logger.error(f"Error analyzing user patterns: {e}")
        
        return {'reasons': reasons, 'actions': actions}
    
    async def _validate_device_consistency(self, user_id: int, device_info: Dict[str, str]) -> Dict[str, Any]:
        """Validate device consistency"""
        reasons = []
        actions = []
        
        try:
            # Get user's device history
            async with db_manager.get_connection() as conn:
                # Check if user has multiple devices (basic check)
                device_history = await conn.fetch(
                    """
                    SELECT DISTINCT device_fingerprint 
                    FROM study_sessions 
                    WHERE user_id = $1 AND session_date >= CURRENT_DATE - INTERVAL '7 days'
                    """,
                    user_id
                )
                
                if len(device_history) > 3:
                    reasons.append(f"Multiple devices detected: {len(device_history)}")
                    actions.append("FLAG_MULTIPLE_DEVICES")
                
                # Check for rapid device switching
                recent_sessions = await conn.fetch(
                    """
                    SELECT device_fingerprint, session_date
                    FROM study_sessions 
                    WHERE user_id = $1 AND session_date >= CURRENT_DATE - INTERVAL '1 day'
                    ORDER BY session_date DESC
                    LIMIT 10
                    """,
                    user_id
                )
                
                if len(recent_sessions) > 5:
                    devices = [row['device_fingerprint'] for row in recent_sessions]
                    unique_devices = len(set(devices))
                    if unique_devices > 2:
                        reasons.append("Rapid device switching detected")
                        actions.append("FLAG_DEVICE_SWITCHING")
        
        except Exception as e:
            self.logger.error(f"Error validating device consistency: {e}")
        
        return {'reasons': reasons, 'actions': actions}
    
    async def _analyze_time_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze time-based patterns"""
        reasons = []
        actions = []
        
        try:
            async with db_manager.get_connection() as conn:
                # Get session times
                sessions = await conn.fetch(
                    """
                    SELECT start_time, end_time, duration_minutes
                    FROM study_sessions 
                    WHERE user_id = $1 AND session_date >= CURRENT_DATE - INTERVAL '7 days'
                    ORDER BY start_time DESC
                    """,
                    user_id
                )
                
                if len(sessions) < 3:
                    return {'reasons': reasons, 'actions': actions}
                
                # Check for unrealistic study hours
                night_sessions = 0
                for session in sessions:
                    hour = session['start_time'].hour
                    if hour < 6 or hour > 23:  # Night sessions
                        night_sessions += 1
                
                if night_sessions > len(sessions) * 0.7:
                    reasons.append("Excessive night-time study sessions")
                    actions.append("FLAG_NIGHT_STUDY")
                
                # Check for too frequent sessions
                if len(sessions) > 10:
                    # Check for sessions too close together
                    for i in range(1, len(sessions)):
                        time_diff = sessions[i-1]['start_time'] - sessions[i]['end_time']
                        if time_diff.total_seconds() < 300:  # Less than 5 minutes
                            reasons.append("Sessions too close together")
                            actions.append("FLAG_FREQUENT_SESSIONS")
                            break
        
        except Exception as e:
            self.logger.error(f"Error analyzing time patterns: {e}")
        
        return {'reasons': reasons, 'actions': actions}
    
    async def _analyze_performance_patterns(
        self, 
        user_id: int, 
        questions_answered: int, 
        correct_answers: int
    ) -> Dict[str, Any]:
        """Analyze performance patterns"""
        reasons = []
        actions = []
        
        try:
            async with db_manager.get_connection() as conn:
                # Get historical performance
                performance = await conn.fetch(
                    """
                    SELECT correct_answers, total_questions
                    FROM study_reports 
                    WHERE user_id = $1 AND report_date >= CURRENT_DATE - INTERVAL '30 days'
                    AND total_questions > 0
                    ORDER BY report_date DESC
                    """,
                    user_id
                )
                
                if len(performance) < 5:
                    return {'reasons': reasons, 'actions': actions}
                
                # Calculate historical accuracy
                total_correct = sum(row['correct_answers'] for row in performance)
                total_questions = sum(row['total_questions'] for row in performance)
                historical_accuracy = (total_correct / total_questions) * 100
                
                # Check current session accuracy
                if questions_answered > 0:
                    current_accuracy = (correct_answers / questions_answered) * 100
                    
                    # Check for sudden accuracy improvement
                    if current_accuracy > historical_accuracy + 30:
                        reasons.append(f"Sudden accuracy improvement: {current_accuracy:.1f}% vs {historical_accuracy:.1f}%")
                        actions.append("FLAG_ACCURACY_IMPROVEMENT")
                    
                    # Check for perfect accuracy
                    if current_accuracy == 100 and questions_answered > 10:
                        reasons.append("Perfect accuracy with many questions")
                        actions.append("FLAG_PERFECT_ACCURACY")
        
        except Exception as e:
            self.logger.error(f"Error analyzing performance patterns: {e}")
        
        return {'reasons': reasons, 'actions': actions}
    
    def _calculate_risk_level(self, reasons: List[str]) -> Tuple[FraudRiskLevel, bool, float]:
        """Calculate fraud risk level"""
        if not reasons:
            return FraudRiskLevel.LOW, False, 0.0
        
        # Weight different types of flags
        critical_flags = ['FLAG_PERFECT_ACCURACY', 'FLAG_PERFECT_CONSISTENCY', 'FLAG_DEVICE_SWITCHING']
        high_flags = ['FLAG_STUDY_SPIKE', 'FLAG_ANSWERING_SPEED', 'FLAG_MULTIPLE_DEVICES']
        medium_flags = ['FLAG_HIGH_ACCURACY', 'FLAG_SESSION_DURATION', 'FLAG_DAILY_LIMIT']
        
        critical_count = sum(1 for reason in reasons if any(flag in reason for flag in critical_flags))
        high_count = sum(1 for reason in reasons if any(flag in reason for flag in high_flags))
        medium_count = sum(1 for reason in reasons if any(flag in reason for flag in medium_flags))
        
        # Calculate risk level
        if critical_count > 0 or high_count >= 2:
            return FraudRiskLevel.CRITICAL, True, 0.9
        elif high_count > 0 or medium_count >= 3:
            return FraudRiskLevel.HIGH, True, 0.7
        elif medium_count >= 2:
            return FraudRiskLevel.MEDIUM, True, 0.5
        else:
            return FraudRiskLevel.LOW, False, 0.2
    
    async def _get_daily_stats(self, user_id: int) -> Dict[str, Any]:
        """Get daily statistics for user"""
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    """
                    SELECT 
                        COALESCE(SUM(study_minutes), 0) as total_minutes,
                        COUNT(*) as session_count
                    FROM study_reports 
                    WHERE user_id = $1 AND report_date = CURRENT_DATE
                    """,
                    user_id
                )
                
                return {
                    'total_minutes': result['total_minutes'] if result else 0,
                    'session_count': result['session_count'] if result else 0
                }
        except Exception as e:
            self.logger.error(f"Error getting daily stats: {e}")
            return {'total_minutes': 0, 'session_count': 0}
    
    async def _log_fraud_detection(self, result: FraudDetectionResult) -> None:
        """Log fraud detection result"""
        try:
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO fraud_detection_logs 
                    (user_id, is_fraud, risk_level, reasons, confidence, actions_taken, metadata, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                    """,
                    result.metadata['user_id'],
                    result.is_fraud,
                    result.risk_level.value,
                    result.reasons,
                    result.confidence,
                    result.actions_taken,
                    result.metadata
                )
        except Exception as e:
            self.logger.error(f"Error logging fraud detection: {e}")
    
    async def _take_fraud_action(self, user_id: int, result: FraudDetectionResult) -> None:
        """Take action against detected fraud"""
        try:
            # Log the action
            self.logger.warning(f"Fraud detected for user {user_id}: {result.reasons}")
            
            # Mark session as suspicious
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO suspicious_sessions 
                    (user_id, fraud_result, risk_level, created_at)
                    VALUES ($1, $2, $3, NOW())
                    """,
                    user_id,
                    result.reasons,
                    result.risk_level.value
                )
            
            # For critical fraud, temporarily limit user
            if result.risk_level == FraudRiskLevel.CRITICAL:
                await conn.execute(
                    """
                    INSERT INTO user_restrictions 
                    (user_id, restriction_type, reason, expires_at, created_at)
                    VALUES ($1, 'study_limit', $2, NOW() + INTERVAL '24 hours', NOW())
                    """,
                    user_id,
                    f"Fraud detected: {', '.join(result.reasons)}"
                )
        
        except Exception as e:
            self.logger.error(f"Error taking fraud action: {e}")
    
    async def get_user_fraud_history(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's fraud detection history"""
        try:
            async with db_manager.get_connection() as conn:
                results = await conn.fetch(
                    """
                    SELECT * FROM fraud_detection_logs 
                    WHERE user_id = $1 AND created_at >= CURRENT_DATE - INTERVAL '%s days'
                    ORDER BY created_at DESC
                    """,
                    user_id, days
                )
                
                return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"Error getting fraud history: {e}")
            return []
    
    async def is_user_restricted(self, user_id: int) -> bool:
        """Check if user has active restrictions"""
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    """
                    SELECT COUNT(*) as count FROM user_restrictions 
                    WHERE user_id = $1 AND expires_at > NOW()
                    """,
                    user_id
                )
                
                return result['count'] > 0 if result else False
        except Exception as e:
            self.logger.error(f"Error checking user restrictions: {e}")
            return False


# Global instance
anti_fraud_service = AntiFraudService()
