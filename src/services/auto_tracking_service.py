"""
🌌 SarlakBot v3.1.0 - Auto Tracking Service
Automatic study tracking and reporting system
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ActivityType(Enum):
    """Activity types for auto tracking"""
    STUDY_SESSION = "study_session"
    TEST_SESSION = "test_session"
    BREAK_TIME = "break_time"
    IDLE_TIME = "idle_time"
    FOCUS_TIME = "focus_time"
    REVIEW_TIME = "review_time"


@dataclass
class AutoTrackedActivity:
    """Auto tracked activity data"""
    user_id: int
    activity_type: ActivityType
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    subject: str = None
    metadata: Dict[str, Any] = None
    confidence_score: float = 1.0


@dataclass
class StudyPattern:
    """Study pattern data"""
    user_id: int
    pattern_type: str
    frequency: int
    average_duration: float
    preferred_subjects: List[str]
    peak_hours: List[int]
    confidence: float


class AutoTrackingService:
    """
    🌌 Auto Tracking Service
    Automatic study tracking and reporting system
    """
    
    def __init__(self):
        self.logger = logger
        self.tracking_config = {
            'min_session_duration': 5,  # Minimum 5 minutes
            'max_session_duration': 180,  # Maximum 3 hours
            'idle_threshold': 300,  # 5 minutes idle time
            'break_threshold': 600,  # 10 minutes break time
            'confidence_threshold': 0.7,
            'pattern_analysis_days': 30,
            'auto_goal_adjustment': True,
            'smart_notifications': True
        }
    
    async def start_auto_tracking(self, user_id: int) -> bool:
        """Start automatic tracking for a user"""
        try:
            # Check if user already has active tracking
            async with db_manager.get_connection() as conn:
                existing = await conn.fetchrow(
                    """
                    SELECT * FROM auto_tracking_sessions 
                    WHERE user_id = $1 AND is_active = TRUE
                    """,
                    user_id
                )
                
                if existing:
                    self.logger.info(f"User {user_id} already has active tracking")
                    return True
                
                # Start new tracking session
                await conn.execute(
                    """
                    INSERT INTO auto_tracking_sessions 
                    (user_id, start_time, is_active, tracking_config)
                    VALUES ($1, NOW(), TRUE, $2)
                    """,
                    user_id, self.tracking_config
                )
                
                self.logger.info(f"Started auto tracking for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error starting auto tracking: {e}")
            return False
    
    async def stop_auto_tracking(self, user_id: int) -> bool:
        """Stop automatic tracking for a user"""
        try:
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    UPDATE auto_tracking_sessions 
                    SET is_active = FALSE, end_time = NOW()
                    WHERE user_id = $1 AND is_active = TRUE
                    """,
                    user_id
                )
                
                self.logger.info(f"Stopped auto tracking for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error stopping auto tracking: {e}")
            return False
    
    async def track_activity(
        self,
        user_id: int,
        activity_type: ActivityType,
        start_time: datetime,
        end_time: datetime,
        subject: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Track a specific activity"""
        try:
            duration_minutes = int((end_time - start_time).total_seconds() / 60)
            
            # Validate activity
            if not self._validate_activity(duration_minutes, activity_type):
                self.logger.warning(f"Invalid activity for user {user_id}: {duration_minutes} minutes")
                return False
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(
                user_id, activity_type, duration_minutes, subject
            )
            
            # Create activity record
            activity = AutoTrackedActivity(
                user_id=user_id,
                activity_type=activity_type,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration_minutes,
                subject=subject,
                metadata=metadata or {},
                confidence_score=confidence
            )
            
            # Save activity
            await self._save_activity(activity)
            
            # Update study report
            await self._update_study_report(activity)
            
            # Update user patterns
            await self._update_user_patterns(activity)
            
            # Check for achievements
            await self._check_achievements(user_id, activity)
            
            # Send smart notifications
            if self.tracking_config['smart_notifications']:
                await self._send_smart_notification(user_id, activity)
            
            self.logger.info(f"Tracked activity for user {user_id}: {activity_type.value} - {duration_minutes} minutes")
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking activity: {e}")
            return False
    
    async def detect_study_sessions(self, user_id: int) -> List[AutoTrackedActivity]:
        """Detect study sessions from user activity"""
        try:
            # Get user's recent activity
            async with db_manager.get_connection() as conn:
                activities = await conn.fetch(
                    """
                    SELECT * FROM user_activities 
                    WHERE user_id = $1 
                    AND activity_time >= NOW() - INTERVAL '24 hours'
                    ORDER BY activity_time ASC
                    """,
                    user_id
                )
            
            if not activities:
                return []
            
            # Analyze activity patterns
            study_sessions = []
            current_session = None
            
            for activity in activities:
                activity_type = self._classify_activity(activity)
                
                if activity_type == ActivityType.STUDY_SESSION:
                    if current_session is None:
                        current_session = {
                            'start_time': activity['activity_time'],
                            'end_time': activity['activity_time'],
                            'activities': [activity]
                        }
                    else:
                        current_session['end_time'] = activity['activity_time']
                        current_session['activities'].append(activity)
                else:
                    if current_session:
                        # End current session
                        duration = (current_session['end_time'] - current_session['start_time']).total_seconds() / 60
                        if duration >= self.tracking_config['min_session_duration']:
                            study_sessions.append(AutoTrackedActivity(
                                user_id=user_id,
                                activity_type=ActivityType.STUDY_SESSION,
                                start_time=current_session['start_time'],
                                end_time=current_session['end_time'],
                                duration_minutes=int(duration),
                                subject=self._extract_subject(current_session['activities']),
                                metadata={'detected_activities': len(current_session['activities'])}
                            ))
                        current_session = None
            
            # Process final session
            if current_session:
                duration = (current_session['end_time'] - current_session['start_time']).total_seconds() / 60
                if duration >= self.tracking_config['min_session_duration']:
                    study_sessions.append(AutoTrackedActivity(
                        user_id=user_id,
                        activity_type=ActivityType.STUDY_SESSION,
                        start_time=current_session['start_time'],
                        end_time=current_session['end_time'],
                        duration_minutes=int(duration),
                        subject=self._extract_subject(current_session['activities']),
                        metadata={'detected_activities': len(current_session['activities'])}
                    ))
            
            return study_sessions
            
        except Exception as e:
            self.logger.error(f"Error detecting study sessions: {e}")
            return []
    
    async def generate_auto_report(self, user_id: int, report_date: date = None) -> Dict[str, Any]:
        """Generate automatic study report"""
        try:
            if report_date is None:
                report_date = date.today()
            
            # Get tracked activities for the day
            async with db_manager.get_connection() as conn:
                activities = await conn.fetch(
                    """
                    SELECT * FROM auto_tracked_activities 
                    WHERE user_id = $1 AND DATE(start_time) = $2
                    ORDER BY start_time ASC
                    """,
                    user_id, report_date
                )
            
            if not activities:
                return {
                    'date': report_date,
                    'total_study_time': 0,
                    'sessions_count': 0,
                    'subjects_studied': [],
                    'focus_score': 0.0,
                    'break_time': 0,
                    'achievements_unlocked': [],
                    'goals_progress': {},
                    'recommendations': []
                }
            
            # Analyze activities
            total_study_time = 0
            sessions_count = 0
            subjects = set()
            focus_times = []
            break_times = []
            achievements = []
            
            for activity in activities:
                if activity['activity_type'] == 'study_session':
                    total_study_time += activity['duration_minutes']
                    sessions_count += 1
                    if activity['subject']:
                        subjects.add(activity['subject'])
                    focus_times.append(activity['duration_minutes'])
                elif activity['activity_type'] == 'break_time':
                    break_times.append(activity['duration_minutes'])
            
            # Calculate focus score
            focus_score = self._calculate_focus_score(focus_times)
            
            # Get achievements unlocked today
            achievements = await self._get_daily_achievements(user_id, report_date)
            
            # Get goals progress
            goals_progress = await self._get_goals_progress(user_id, report_date)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(user_id, activities)
            
            return {
                'date': report_date,
                'total_study_time': total_study_time,
                'sessions_count': sessions_count,
                'subjects_studied': list(subjects),
                'focus_score': focus_score,
                'break_time': sum(break_times),
                'achievements_unlocked': achievements,
                'goals_progress': goals_progress,
                'recommendations': recommendations,
                'detailed_activities': [dict(activity) for activity in activities]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating auto report: {e}")
            return {}
    
    async def analyze_study_patterns(self, user_id: int) -> List[StudyPattern]:
        """Analyze user's study patterns"""
        try:
            async with db_manager.get_connection() as conn:
                # Get user's study history
                activities = await conn.fetch(
                    """
                    SELECT * FROM auto_tracked_activities 
                    WHERE user_id = $1 
                    AND start_time >= NOW() - INTERVAL '%s days'
                    ORDER BY start_time ASC
                    """,
                    user_id, self.tracking_config['pattern_analysis_days']
                )
            
            if not activities:
                return []
            
            # Analyze patterns
            patterns = []
            
            # Daily pattern
            daily_pattern = self._analyze_daily_pattern(activities)
            if daily_pattern:
                patterns.append(daily_pattern)
            
            # Subject pattern
            subject_pattern = self._analyze_subject_pattern(activities)
            if subject_pattern:
                patterns.append(subject_pattern)
            
            # Time pattern
            time_pattern = self._analyze_time_pattern(activities)
            if time_pattern:
                patterns.append(time_pattern)
            
            # Duration pattern
            duration_pattern = self._analyze_duration_pattern(activities)
            if duration_pattern:
                patterns.append(duration_pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing study patterns: {e}")
            return []
    
    async def auto_adjust_goals(self, user_id: int) -> bool:
        """Automatically adjust user's study goals based on patterns"""
        try:
            if not self.tracking_config['auto_goal_adjustment']:
                return False
            
            # Get user's current goals
            async with db_manager.get_connection() as conn:
                goals = await conn.fetch(
                    """
                    SELECT * FROM study_goals 
                    WHERE user_id = $1 AND is_active = TRUE
                    """,
                    user_id
                )
            
            if not goals:
                return False
            
            # Analyze recent performance
            patterns = await self.analyze_study_patterns(user_id)
            
            for goal in goals:
                new_target = self._calculate_optimal_goal(goal, patterns)
                
                if new_target != goal['goal_target']:
                    await conn.execute(
                        """
                        UPDATE study_goals 
                        SET goal_target = $1, updated_at = NOW()
                        WHERE goal_id = $2
                        """,
                        new_target, goal['goal_id']
                    )
                    
                    self.logger.info(f"Adjusted goal {goal['goal_id']} for user {user_id}: {goal['goal_target']} -> {new_target}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error auto adjusting goals: {e}")
            return False
    
    def _validate_activity(self, duration_minutes: int, activity_type: ActivityType) -> bool:
        """Validate activity duration and type"""
        if duration_minutes < 1:
            return False
        
        if activity_type == ActivityType.STUDY_SESSION:
            return (self.tracking_config['min_session_duration'] <= 
                   duration_minutes <= 
                   self.tracking_config['max_session_duration'])
        
        return True
    
    def _calculate_confidence_score(
        self, 
        user_id: int, 
        activity_type: ActivityType, 
        duration_minutes: int, 
        subject: str
    ) -> float:
        """Calculate confidence score for tracked activity"""
        confidence = 1.0
        
        # Duration confidence
        if activity_type == ActivityType.STUDY_SESSION:
            if duration_minutes < 10:
                confidence *= 0.8
            elif duration_minutes > 120:
                confidence *= 0.9
        
        # Subject confidence
        if subject and len(subject) < 3:
            confidence *= 0.7
        
        # Time confidence (study during normal hours)
        # This would need actual time analysis
        
        return min(confidence, 1.0)
    
    async def _save_activity(self, activity: AutoTrackedActivity) -> None:
        """Save tracked activity to database"""
        async with db_manager.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO auto_tracked_activities 
                (user_id, activity_type, start_time, end_time, duration_minutes, 
                 subject, metadata, confidence_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                activity.user_id, activity.activity_type.value, activity.start_time,
                activity.end_time, activity.duration_minutes, activity.subject,
                activity.metadata, activity.confidence_score
            )
    
    async def _update_study_report(self, activity: AutoTrackedActivity) -> None:
        """Update study report with tracked activity"""
        if activity.activity_type == ActivityType.STUDY_SESSION:
            from src.services.report_service import report_service
            
            await report_service.update_study_report(
                user_id=activity.user_id,
                study_minutes=activity.duration_minutes,
                subjects_studied=[activity.subject] if activity.subject else [],
                study_sessions=1
            )
    
    async def _update_user_patterns(self, activity: AutoTrackedActivity) -> None:
        """Update user study patterns"""
        # This would update user's study patterns in the database
        pass
    
    async def _check_achievements(self, user_id: int, activity: AutoTrackedActivity) -> None:
        """Check for new achievements based on activity"""
        # This would check and unlock new achievements
        pass
    
    async def _send_smart_notification(self, user_id: int, activity: AutoTrackedActivity) -> None:
        """Send smart notification based on activity"""
        # This would send contextual notifications
        pass
    
    def _classify_activity(self, activity: Dict[str, Any]) -> ActivityType:
        """Classify activity type based on data"""
        # This would analyze activity data to determine type
        return ActivityType.STUDY_SESSION
    
    def _extract_subject(self, activities: List[Dict[str, Any]]) -> str:
        """Extract subject from activities"""
        # This would analyze activities to determine subject
        return "عمومی"
    
    def _calculate_focus_score(self, focus_times: List[int]) -> float:
        """Calculate focus score based on session durations"""
        if not focus_times:
            return 0.0
        
        # Longer sessions indicate better focus
        avg_duration = sum(focus_times) / len(focus_times)
        return min(avg_duration / 60, 1.0)  # Normalize to 0-1
    
    async def _get_daily_achievements(self, user_id: int, report_date: date) -> List[Dict[str, Any]]:
        """Get achievements unlocked today"""
        # This would return daily achievements
        return []
    
    async def _get_goals_progress(self, user_id: int, report_date: date) -> Dict[str, Any]:
        """Get goals progress for the day"""
        # This would return goals progress
        return {}
    
    async def _generate_recommendations(self, user_id: int, activities: List[Dict[str, Any]]) -> List[str]:
        """Generate study recommendations"""
        recommendations = []
        
        # Analyze activities and generate recommendations
        if not activities:
            recommendations.append("شروع به مطالعه کنید تا پیشرفت خود را پیگیری کنید!")
        
        return recommendations
    
    def _analyze_daily_pattern(self, activities: List[Dict[str, Any]]) -> Optional[StudyPattern]:
        """Analyze daily study pattern"""
        # This would analyze daily patterns
        return None
    
    def _analyze_subject_pattern(self, activities: List[Dict[str, Any]]) -> Optional[StudyPattern]:
        """Analyze subject study pattern"""
        # This would analyze subject patterns
        return None
    
    def _analyze_time_pattern(self, activities: List[Dict[str, Any]]) -> Optional[StudyPattern]:
        """Analyze time-based study pattern"""
        # This would analyze time patterns
        return None
    
    def _analyze_duration_pattern(self, activities: List[Dict[str, Any]]) -> Optional[StudyPattern]:
        """Analyze duration pattern"""
        # This would analyze duration patterns
        return None
    
    def _calculate_optimal_goal(self, goal: Dict[str, Any], patterns: List[StudyPattern]) -> int:
        """Calculate optimal goal based on patterns"""
        # This would calculate optimal goal
        return goal['goal_target']


# Global instance
auto_tracking_service = AutoTrackingService()
