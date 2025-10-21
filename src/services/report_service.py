"""
🌌 SarlakBot v3.1.0 - Report Service
Complete study report and tracking system
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class StudyReport:
    """Study report data structure"""
    user_id: int
    report_date: date
    study_minutes: int = 0
    tests_count: int = 0
    correct_answers: int = 0
    total_questions: int = 0
    subjects_studied: List[str] = None
    study_sessions: int = 0
    break_time_minutes: int = 0
    focus_score: float = 0.0

    def __post_init__(self):
        if self.subjects_studied is None:
            self.subjects_studied = []


@dataclass
class StudyStatistics:
    """Study statistics data structure"""
    total_study_minutes: int
    total_tests: int
    total_questions: int
    correct_answers: int
    accuracy_rate: float
    average_session_minutes: float
    study_days: int
    current_streak: int


@dataclass
class StudyGoal:
    """Study goal data structure"""
    goal_id: int
    user_id: int
    goal_type: str  # daily, weekly, monthly
    goal_target: int
    goal_unit: str  # minutes, questions, tests
    goal_period_start: date
    goal_period_end: date
    current_progress: int = 0
    is_completed: bool = False


class ReportService:
    """
    🌌 Report Service
    Complete study report and tracking system
    """
    
    def __init__(self):
        self.logger = logger
    
    async def get_today_report(self, user_id: int) -> Optional[StudyReport]:
        """Fetch today's aggregated study report for a user"""
        try:
            async with db_manager.get_connection() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT 
                        COALESCE(SUM(study_minutes), 0) AS study_minutes,
                        COALESCE(SUM(tests_count), 0) AS tests_count,
                        COALESCE(SUM(correct_answers), 0) AS correct_answers,
                        COALESCE(SUM(total_questions), 0) AS total_questions,
                        COALESCE(COUNT(*), 0) AS study_sessions
                    FROM study_reports
                    WHERE user_id = $1 AND report_date = CURRENT_DATE
                    """,
                    user_id
                )
                if not row:
                    return None
                return StudyReport(
                    user_id=user_id,
                    report_date=date.today(),
                    study_minutes=row['study_minutes'],
                    tests_count=row['tests_count'],
                    correct_answers=row['correct_answers'],
                    total_questions=row['total_questions'],
                    subjects_studied=[],
                    study_sessions=row['study_sessions']
                )
        except Exception as e:
            self.logger.error(f"Error get_today_report: {e}")
            return None

    async def get_weekly_summary(self, user_id: int) -> Dict[str, Any]:
        """Weekly summary for last 7 days"""
        try:
            async with db_manager.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT report_date, 
                           COALESCE(SUM(study_minutes),0) AS study_minutes,
                           COALESCE(SUM(tests_count),0) AS tests_count
                    FROM study_reports
                    WHERE user_id = $1 AND report_date >= CURRENT_DATE - INTERVAL '6 days'
                    GROUP BY report_date
                    ORDER BY report_date ASC
                    """,
                    user_id
                )
                daily = [
                    {
                        'report_date': r['report_date'],
                        'study_minutes': r['study_minutes'],
                        'tests_count': r['tests_count'],
                    } for r in rows
                ]
                total_minutes = sum(d['study_minutes'] for d in daily)
                total_tests = sum(d['tests_count'] for d in daily)
                study_days = sum(1 for d in daily if d['study_minutes'] > 0)
                avg = round(total_minutes / max(len(daily), 1), 1)
                return {
                    'daily_data': daily,
                    'total_minutes': total_minutes,
                    'total_tests': total_tests,
                    'study_days': study_days,
                    'average_daily': avg,
                }
        except Exception as e:
            self.logger.error(f"Error get_weekly_summary: {e}")
            return {'daily_data': [], 'total_minutes': 0, 'total_tests': 0, 'study_days': 0, 'average_daily': 0}

    async def get_monthly_summary(self, user_id: int) -> Dict[str, Any]:
        """Monthly summary for last 30 days"""
        try:
            async with db_manager.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT subject, 
                           COALESCE(SUM(study_minutes),0) AS study_minutes,
                           GREATEST(ROUND(100.0 * NULLIF(SUM(correct_answers),0) / NULLIF(SUM(total_questions),0), 1), 0) AS accuracy
                    FROM study_reports
                    WHERE user_id = $1 AND report_date >= CURRENT_DATE - INTERVAL '29 days'
                    GROUP BY subject
                    ORDER BY study_minutes DESC NULLS LAST
                    """,
                    user_id
                )
                top_subjects = [
                    {
                        'subject': (r['subject'] or 'نامشخص'),
                        'study_minutes': r['study_minutes'],
                        'accuracy_rate': float(r['accuracy'] or 0.0)
                    } for r in rows
                ]
                totals = await conn.fetchrow(
                    """
                    SELECT 
                        COALESCE(SUM(study_minutes),0) AS total_minutes,
                        COALESCE(SUM(tests_count),0) AS total_tests,
                        COALESCE(SUM(correct_answers),0) AS ca,
                        COALESCE(SUM(total_questions),0) AS tq,
                        COUNT(DISTINCT report_date) AS days
                    FROM study_reports
                    WHERE user_id = $1 AND report_date >= CURRENT_DATE - INTERVAL '29 days'
                    """,
                    user_id
                )
                acc = float(round(100.0 * (totals['ca'] or 0) / max((totals['tq'] or 1), 1), 1))
                return {
                    'total_minutes': totals['total_minutes'],
                    'total_tests': totals['total_tests'],
                    'study_days': totals['days'],
                    'accuracy_rate': acc,
                    'top_subjects': top_subjects,
                }
        except Exception as e:
            self.logger.error(f"Error get_monthly_summary: {e}")
            return {'total_minutes': 0, 'total_tests': 0, 'study_days': 0, 'accuracy_rate': 0.0, 'top_subjects': []}

    async def get_subject_statistics(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Subject-wise statistics for last N days"""
        try:
            async with db_manager.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT subject, 
                           COALESCE(SUM(study_minutes),0) AS study_minutes,
                           COALESCE(SUM(tests_count),0) AS tests_count,
                           GREATEST(ROUND(100.0 * NULLIF(SUM(correct_answers),0) / NULLIF(SUM(total_questions),0), 1), 0) AS accuracy
                    FROM study_reports
                    WHERE user_id = $1 AND report_date >= CURRENT_DATE - ($2::int || ' days')::interval
                    GROUP BY subject
                    ORDER BY study_minutes DESC NULLS LAST
                    """,
                    user_id, days
                )
                return [
                    {
                        'subject': (r['subject'] or 'نامشخص'),
                        'study_minutes': r['study_minutes'],
                        'tests_count': r['tests_count'],
                        'accuracy_rate': float(r['accuracy'] or 0.0)
                    } for r in rows
                ]
        except Exception as e:
            self.logger.error(f"Error get_subject_statistics: {e}")
            return []

    async def log_study_session(self, user_id: int, duration_minutes: int, subject: str, session_type: str = 'study') -> bool:
        """Insert a quick study session and update aggregates"""
        try:
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO study_reports
                    (user_id, report_date, study_minutes, tests_count, correct_answers, total_questions, subject, start_time, end_time, duration_minutes, activity_type, created_at, updated_at)
                    VALUES ($1, CURRENT_DATE, $2, 0, 0, 0, $3, NOW() - make_interval(mins => $2), NOW(), $2, $4, NOW(), NOW())
                    """,
                    user_id, duration_minutes, subject, session_type
                )
            return True
        except Exception as e:
            self.logger.error(f"Error log_study_session: {e}")
            return False

    async def ensure_default_daily_goal(self, user_id: int, target_minutes: int = 120) -> bool:
        """Ensure a simple default daily goal exists"""
        try:
            async with db_manager.get_connection() as conn:
                exists = await conn.fetchval(
                    """
                    SELECT 1 FROM study_goals
                    WHERE user_id = $1 AND goal_type = 'daily' AND goal_unit = 'minutes'
                    """,
                    user_id
                )
                if exists:
                    return False
                await conn.execute(
                    """
                    INSERT INTO study_goals (user_id, goal_type, goal_target, goal_unit, goal_period_start, goal_period_end, current_progress, is_completed)
                    VALUES ($1, 'daily', $2, 'minutes', CURRENT_DATE, CURRENT_DATE, 0, FALSE)
                    """,
                    user_id, target_minutes
                )
                return True
        except Exception as e:
            self.logger.error(f"Error ensure_default_daily_goal: {e}")
            return False

    async def get_goals_progress(self, user_id: int) -> List[Dict[str, Any]]:
        """Return simple goals progress for the current period"""
        try:
            async with db_manager.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT goal_id, goal_type, goal_target, goal_unit, current_progress,
                           CASE WHEN goal_target > 0 THEN ROUND(100.0 * current_progress / goal_target, 1) ELSE 0 END AS percent
                    FROM study_goals
                    WHERE user_id = $1 AND goal_type = 'daily' AND goal_period_start = CURRENT_DATE
                    ORDER BY goal_id ASC
                    """,
                    user_id
                )
                return [
                    {
                        'goal_id': r['goal_id'],
                        'title': f"{r['goal_type']} {r['goal_unit']}",
                        'target': r['goal_target'],
                        'current': r['current_progress'],
                        'percent': float(r['percent'] or 0.0)
                    } for r in rows
                ]
        except Exception as e:
            self.logger.error(f"Error get_goals_progress: {e}")
            return []
    async def update_study_report(
        self, 
        user_id: int, 
        study_minutes: int = 0,
        tests_count: int = 0,
        correct_answers: int = 0,
        total_questions: int = 0,
        subjects_studied: List[str] = None,
        study_sessions: int = 1,
        report_date: date = None
    ) -> bool:
        """Update or create study report for a user"""
        try:
            if report_date is None:
                report_date = date.today()
            
            if subjects_studied is None:
                subjects_studied = []
            
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    "SELECT update_study_report($1, $2, $3, $4, $5, $6, $7, $8)",
                    user_id, report_date, study_minutes, tests_count,
                    correct_answers, total_questions, subjects_studied, study_sessions
                )
            
            self.logger.info(f"Updated study report for user {user_id} on {report_date}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating study report: {e}")
            return False
    
    async def get_study_statistics(self, user_id: int, days: int = 30) -> Optional[StudyStatistics]:
        """Get comprehensive study statistics for a user"""
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    "SELECT * FROM get_study_statistics($1, $2)",
                    user_id, days
                )
                
                if result:
                    return StudyStatistics(
                        total_study_minutes=result['total_study_minutes'],
                        total_tests=result['total_tests'],
                        total_questions=result['total_questions'],
                        correct_answers=result['correct_answers'],
                        accuracy_rate=float(result['accuracy_rate']),
                        average_session_minutes=float(result['average_session_minutes']),
                        study_days=result['study_days'],
                        current_streak=result['current_streak']
                    )
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting study statistics: {e}")
            return None
    
    async def get_daily_progress(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily progress data for charts"""
        try:
            async with db_manager.get_connection() as conn:
                results = await conn.fetch(
                    "SELECT * FROM get_daily_progress($1, $2)",
                    user_id, days
                )
                
                return [dict(row) for row in results]
                
        except Exception as e:
            self.logger.error(f"Error getting daily progress: {e}")
            return []
    
    async def get_subject_statistics(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get subject-wise statistics"""
        try:
            async with db_manager.get_connection() as conn:
                results = await conn.fetch(
                    "SELECT * FROM get_subject_statistics($1, $2)",
                    user_id, days
                )
                
                return [dict(row) for row in results]
                
        except Exception as e:
            self.logger.error(f"Error getting subject statistics: {e}")
            return []
    
    async def get_today_report(self, user_id: int) -> Optional[StudyReport]:
        """Get today's study report"""
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    """
                    SELECT * FROM study_reports 
                    WHERE user_id = $1 AND report_date = CURRENT_DATE
                    """,
                    user_id
                )
                
                if result:
                    return StudyReport(
                        user_id=result['user_id'],
                        report_date=result['report_date'],
                        study_minutes=result['study_minutes'],
                        tests_count=result['tests_count'],
                        correct_answers=result['correct_answers'],
                        total_questions=result['total_questions'],
                        subjects_studied=result['subjects_studied'] or [],
                        study_sessions=result['study_sessions'],
                        break_time_minutes=result['break_time_minutes'],
                        focus_score=float(result['focus_score'])
                    )
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting today's report: {e}")
            return None
    
    async def create_study_goal(
        self,
        user_id: int,
        goal_type: str,
        goal_target: int,
        goal_unit: str,
        goal_period_start: date = None,
        goal_period_end: date = None
    ) -> bool:
        """Create a new study goal"""
        try:
            if goal_period_start is None:
                goal_period_start = date.today()
            
            if goal_period_end is None:
                if goal_type == 'daily':
                    goal_period_end = goal_period_start
                elif goal_type == 'weekly':
                    goal_period_end = goal_period_start + timedelta(days=6)
                elif goal_type == 'monthly':
                    goal_period_end = goal_period_start + timedelta(days=30)
            
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO study_goals 
                    (user_id, goal_type, goal_target, goal_unit, goal_period_start, goal_period_end)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    user_id, goal_type, goal_target, goal_unit, goal_period_start, goal_period_end
                )
            
            self.logger.info(f"Created study goal for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating study goal: {e}")
            return False
    
    async def get_study_goals(self, user_id: int, goal_type: str = None) -> List[StudyGoal]:
        """Get user's study goals"""
        try:
            async with db_manager.get_connection() as conn:
                if goal_type:
                    results = await conn.fetch(
                        """
                        SELECT * FROM study_goals 
                        WHERE user_id = $1 AND goal_type = $2
                        ORDER BY created_at DESC
                        """,
                        user_id, goal_type
                    )
                else:
                    results = await conn.fetch(
                        """
                        SELECT * FROM study_goals 
                        WHERE user_id = $1
                        ORDER BY created_at DESC
                        """,
                        user_id
                    )
                
                goals = []
                for row in results:
                    goals.append(StudyGoal(
                        goal_id=row['goal_id'],
                        user_id=row['user_id'],
                        goal_type=row['goal_type'],
                        goal_target=row['goal_target'],
                        goal_unit=row['goal_unit'],
                        goal_period_start=row['goal_period_start'],
                        goal_period_end=row['goal_period_end'],
                        current_progress=row['current_progress'],
                        is_completed=row['is_completed']
                    ))
                
                return goals
                
        except Exception as e:
            self.logger.error(f"Error getting study goals: {e}")
            return []
    
    async def update_goal_progress(self, goal_id: int, progress: int) -> bool:
        """Update goal progress"""
        try:
            async with db_manager.get_connection() as conn:
                # Get goal details
                goal = await conn.fetchrow(
                    "SELECT * FROM study_goals WHERE goal_id = $1",
                    goal_id
                )
                
                if not goal:
                    return False
                
                new_progress = goal['current_progress'] + progress
                is_completed = new_progress >= goal['goal_target']
                
                await conn.execute(
                    """
                    UPDATE study_goals 
                    SET current_progress = $1, is_completed = $2, updated_at = NOW()
                    WHERE goal_id = $3
                    """,
                    new_progress, is_completed, goal_id
                )
                
                self.logger.info(f"Updated goal {goal_id} progress to {new_progress}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating goal progress: {e}")
            return False
    
    async def get_weekly_summary(self, user_id: int) -> Dict[str, Any]:
        """Get weekly study summary"""
        try:
            stats = await self.get_study_statistics(user_id, 7)
            daily_progress = await self.get_daily_progress(user_id, 7)
            
            if not stats:
                return {
                    'total_minutes': 0,
                    'total_tests': 0,
                    'study_days': 0,
                    'average_daily': 0,
                    'daily_data': []
                }
            
            return {
                'total_minutes': stats.total_study_minutes,
                'total_tests': stats.total_tests,
                'study_days': stats.study_days,
                'average_daily': round(stats.total_study_minutes / 7, 1),
                'daily_data': daily_progress
            }
            
        except Exception as e:
            self.logger.error(f"Error getting weekly summary: {e}")
            return {
                'total_minutes': 0,
                'total_tests': 0,
                'study_days': 0,
                'average_daily': 0,
                'daily_data': []
            }
    
    async def get_monthly_summary(self, user_id: int) -> Dict[str, Any]:
        """Get monthly study summary"""
        try:
            stats = await self.get_study_statistics(user_id, 30)
            subject_stats = await self.get_subject_statistics(user_id, 30)
            
            if not stats:
                return {
                    'total_minutes': 0,
                    'total_tests': 0,
                    'study_days': 0,
                    'accuracy_rate': 0,
                    'top_subjects': []
                }
            
            # Get top 3 subjects
            top_subjects = subject_stats[:3] if subject_stats else []
            
            return {
                'total_minutes': stats.total_study_minutes,
                'total_tests': stats.total_tests,
                'study_days': stats.study_days,
                'accuracy_rate': stats.accuracy_rate,
                'top_subjects': top_subjects
            }
            
        except Exception as e:
            self.logger.error(f"Error getting monthly summary: {e}")
            return {
                'total_minutes': 0,
                'study_days': 0,
                'accuracy_rate': 0,
                'top_subjects': []
            }
    
    async def log_study_session(
        self,
        user_id: int,
        duration_minutes: int,
        subject: str = None,
        session_type: str = 'study',
        questions_answered: int = 0,
        correct_answers: int = 0,
        notes: str = None
    ) -> bool:
        """Log a study session"""
        try:
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO study_sessions 
                    (user_id, session_date, start_time, end_time, duration_minutes, 
                     subject, session_type, questions_answered, correct_answers, notes)
                    VALUES ($1, CURRENT_DATE, NOW() - INTERVAL '%s minutes', NOW(), $2, $3, $4, $5, $6, $7)
                    """,
                    user_id, duration_minutes, subject, session_type, 
                    questions_answered, correct_answers, notes
                )
            
            # Update daily report
            await self.update_study_report(
                user_id=user_id,
                study_minutes=duration_minutes,
                correct_answers=correct_answers,
                total_questions=questions_answered,
                subjects_studied=[subject] if subject else [],
                study_sessions=1
            )
            
            self.logger.info(f"Logged study session for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging study session: {e}")
            return False


# Global instance
report_service = ReportService()
