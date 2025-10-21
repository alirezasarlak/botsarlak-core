"""
🌌 SarlakBot v3.1.0 - User Learning Service
Advanced user learning and personalization system
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class LearningLevel(Enum):
    """User learning level enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class InterestArea(Enum):
    """User interest area enumeration"""
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    LITERATURE = "literature"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    ENGLISH = "english"
    RELIGION = "religion"
    PSYCHOLOGY = "psychology"
    COUNSELING = "counseling"
    MOTIVATION = "motivation"


@dataclass
class UserLearningProfile:
    """User learning profile data structure"""
    user_id: int
    learning_level: LearningLevel
    interest_areas: List[InterestArea]
    study_preferences: Dict[str, Any]
    question_patterns: Dict[str, Any]
    response_preferences: Dict[str, Any]
    learning_goals: List[str]
    strengths: List[str]
    weaknesses: List[str]
    last_updated: datetime


@dataclass
class LearningInsight:
    """Learning insight data structure"""
    insight_id: int
    user_id: int
    insight_type: str
    insight_data: Dict[str, Any]
    confidence_score: float
    created_at: datetime


class UserLearningService:
    """
    🌌 User Learning Service
    Advanced user learning and personalization system
    """
    
    def __init__(self):
        self.logger = logger
        
        # Learning configuration
        self.learning_config = {
            'min_questions_for_analysis': 5,
            'analysis_window_days': 30,
            'confidence_threshold': 0.7,
            'update_frequency_hours': 24
        }
        
        # Interest area keywords
        self.interest_keywords = {
            InterestArea.MATHEMATICS: [
                'ریاضی', 'محاسبه', 'حل', 'فرمول', 'معادله', 'جبر', 'هندسه', 'حساب', 'آمار'
            ],
            InterestArea.PHYSICS: [
                'فیزیک', 'نیرو', 'حرکت', 'انرژی', 'مکانیک', 'الکتریسیته', 'مغناطیس', 'نور', 'صدا'
            ],
            InterestArea.CHEMISTRY: [
                'شیمی', 'واکنش', 'ترکیب', 'مولکول', 'اتم', 'جدول تناوبی', 'اسید', 'باز', 'کاتالیزور'
            ],
            InterestArea.BIOLOGY: [
                'زیست', 'سلول', 'ژن', 'تکامل', 'گیاه', 'حیوان', 'انسان', 'دستگاه', 'ارگان'
            ],
            InterestArea.LITERATURE: [
                'ادبیات', 'شعر', 'نثر', 'داستان', 'نویسنده', 'شاعر', 'کتاب', 'رمان', 'نقد'
            ],
            InterestArea.HISTORY: [
                'تاریخ', 'تاریخی', 'دوره', 'دودمان', 'جنگ', 'انقلاب', 'تمدن', 'فرهنگ', 'سیاست'
            ],
            InterestArea.GEOGRAPHY: [
                'جغرافیا', 'کشور', 'شهر', 'آب و هوا', 'نقشه', 'اقلیم', 'جمعیت', 'اقتصاد', 'طبیعت'
            ],
            InterestArea.ENGLISH: [
                'انگلیسی', 'grammar', 'vocabulary', 'تلفظ', 'زبان', 'مکالمه', 'نوشتن', 'خواندن'
            ],
            InterestArea.RELIGION: [
                'دین', 'مذهبی', 'اخلاق', 'احکام', 'قرآن', 'حدیث', 'عبادت', 'ایمان', 'اخلاقی'
            ],
            InterestArea.PSYCHOLOGY: [
                'روانشناسی', 'ذهن', 'رفتار', 'شخصیت', 'روان', 'عاطفه', 'شناخت', 'یادگیری'
            ],
            InterestArea.COUNSELING: [
                'مشاوره', 'راهنمایی', 'انتخاب', 'برنامه', 'مشاور', 'راهنمایی', 'کمک', 'پشتیبانی'
            ],
            InterestArea.MOTIVATION: [
                'انگیزه', 'انگیزشی', 'تشویق', 'انگیزه', 'انگیزه‌دهنده', 'مثبت', 'تشویق', 'انگیزش'
            ]
        }
    
    async def analyze_user_learning_patterns(self, user_id: int) -> Optional[UserLearningProfile]:
        """Analyze user learning patterns and create/update profile"""
        try:
            # Get user's recent questions and interactions
            questions = await self._get_user_recent_questions(user_id)
            
            if len(questions) < self.learning_config['min_questions_for_analysis']:
                self.logger.info(f"Not enough questions for analysis: {len(questions)}")
                return None
            
            # Analyze interest areas
            interest_areas = await self._analyze_interest_areas(questions)
            
            # Analyze learning level
            learning_level = await self._analyze_learning_level(user_id, questions)
            
            # Analyze study preferences
            study_preferences = await self._analyze_study_preferences(user_id, questions)
            
            # Analyze question patterns
            question_patterns = await self._analyze_question_patterns(questions)
            
            # Analyze response preferences
            response_preferences = await self._analyze_response_preferences(user_id)
            
            # Analyze learning goals
            learning_goals = await self._analyze_learning_goals(user_id, questions)
            
            # Analyze strengths and weaknesses
            strengths, weaknesses = await self._analyze_strengths_weaknesses(user_id, questions)
            
            # Create learning profile
            profile = UserLearningProfile(
                user_id=user_id,
                learning_level=learning_level,
                interest_areas=interest_areas,
                study_preferences=study_preferences,
                question_patterns=question_patterns,
                response_preferences=response_preferences,
                learning_goals=learning_goals,
                strengths=strengths,
                weaknesses=weaknesses,
                last_updated=datetime.now()
            )
            
            # Save profile
            await self._save_learning_profile(profile)
            
            # Generate insights
            await self._generate_learning_insights(user_id, profile)
            
            self.logger.info(f"Learning profile updated for user {user_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error analyzing user learning patterns: {e}")
            return None
    
    async def get_personalized_response_context(self, user_id: int, question_text: str) -> Dict[str, Any]:
        """Get personalized context for AI responses"""
        try:
            # Get user learning profile
            profile = await self._get_learning_profile(user_id)
            
            if not profile:
                return self._get_default_context()
            
            # Build personalized context
            context = {
                'user_level': profile.learning_level.value,
                'interest_areas': [area.value for area in profile.interest_areas],
                'study_preferences': profile.study_preferences,
                'learning_goals': profile.learning_goals,
                'strengths': profile.strengths,
                'weaknesses': profile.weaknesses,
                'question_style': profile.question_patterns.get('style', 'formal'),
                'response_preferences': profile.response_preferences
            }
            
            # Add specific context based on question
            question_context = await self._analyze_question_context(question_text, profile)
            context.update(question_context)
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error getting personalized context: {e}")
            return self._get_default_context()
    
    async def get_learning_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get personalized learning recommendations"""
        try:
            profile = await self._get_learning_profile(user_id)
            
            if not profile:
                return []
            
            recommendations = []
            
            # Study time recommendations
            if profile.study_preferences.get('preferred_time') == 'morning':
                recommendations.append({
                    'type': 'study_schedule',
                    'title': 'برنامه مطالعه صبحگاهی',
                    'description': 'بر اساس الگوی شما، مطالعه در صبح برایتان مفیدتر است',
                    'priority': 'high'
                })
            
            # Subject recommendations based on weaknesses
            for weakness in profile.weaknesses:
                recommendations.append({
                    'type': 'subject_focus',
                    'title': f'تمرکز روی {weakness}',
                    'description': f'پیشنهاد می‌کنم زمان بیشتری برای {weakness} اختصاص دهید',
                    'priority': 'medium'
                })
            
            # Interest area recommendations
            for interest in profile.interest_areas:
                recommendations.append({
                    'type': 'interest_development',
                    'title': f'توسعه {interest.value}',
                    'description': f'می‌توانید در زمینه {interest.value} عمیق‌تر مطالعه کنید',
                    'priority': 'low'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting learning recommendations: {e}")
            return []
    
    async def track_learning_progress(self, user_id: int, question_text: str, answer_quality: float) -> None:
        """Track user learning progress"""
        try:
            # Update learning profile based on new interaction
            await self._update_learning_metrics(user_id, question_text, answer_quality)
            
            # Check if profile needs updating
            if await self._should_update_profile(user_id):
                await self.analyze_user_learning_patterns(user_id)
            
        except Exception as e:
            self.logger.error(f"Error tracking learning progress: {e}")
    
    async def _get_user_recent_questions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's recent questions"""
        try:
            query = """
                SELECT 
                    question_id, question_text, question_context, category_id,
                    points_cost, status, created_at
                FROM qa_questions
                WHERE user_id = $1
                AND created_at >= CURRENT_DATE - INTERVAL '1 day' * $2
                ORDER BY created_at DESC
            """
            
            results = await db_manager.fetch_all(
                query, user_id, self.learning_config['analysis_window_days']
            )
            
            return [dict(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error getting user recent questions: {e}")
            return []
    
    async def _analyze_interest_areas(self, questions: List[Dict[str, Any]]) -> List[InterestArea]:
        """Analyze user's interest areas from questions"""
        try:
            interest_scores = {}
            
            for question in questions:
                question_text = question['question_text'].lower()
                
                for area, keywords in self.interest_keywords.items():
                    score = sum(1 for keyword in keywords if keyword in question_text)
                    interest_scores[area] = interest_scores.get(area, 0) + score
            
            # Get top interest areas
            sorted_areas = sorted(interest_scores.items(), key=lambda x: x[1], reverse=True)
            top_areas = [area for area, score in sorted_areas[:5] if score > 0]
            
            return top_areas
            
        except Exception as e:
            self.logger.error(f"Error analyzing interest areas: {e}")
            return []
    
    async def _analyze_learning_level(self, user_id: int, questions: List[Dict[str, Any]]) -> LearningLevel:
        """Analyze user's learning level"""
        try:
            # Get user's study statistics
            query = """
                SELECT 
                    current_level, total_points, total_study_time
                FROM user_levels ul
                LEFT JOIN user_statistics us ON ul.user_id = us.user_id
                WHERE ul.user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if not result:
                return LearningLevel.BEGINNER
            
            level = result['current_level']
            points = result['total_points']
            study_time = result['total_study_time']
            
            # Determine learning level based on metrics
            if level >= 8 and points >= 2000 and study_time >= 1000:
                return LearningLevel.EXPERT
            elif level >= 6 and points >= 1000 and study_time >= 500:
                return LearningLevel.ADVANCED
            elif level >= 4 and points >= 500 and study_time >= 200:
                return LearningLevel.INTERMEDIATE
            else:
                return LearningLevel.BEGINNER
                
        except Exception as e:
            self.logger.error(f"Error analyzing learning level: {e}")
            return LearningLevel.BEGINNER
    
    async def _analyze_study_preferences(self, user_id: int, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's study preferences"""
        try:
            preferences = {
                'question_length': 'medium',
                'detail_level': 'moderate',
                'preferred_time': 'evening',
                'subject_focus': 'balanced'
            }
            
            # Analyze question length preferences
            avg_length = sum(len(q['question_text']) for q in questions) / len(questions)
            if avg_length > 200:
                preferences['question_length'] = 'long'
            elif avg_length < 100:
                preferences['question_length'] = 'short'
            
            # Analyze detail level from question context
            context_questions = [q for q in questions if q['question_context']]
            if len(context_questions) / len(questions) > 0.5:
                preferences['detail_level'] = 'high'
            
            # Analyze preferred time from question timestamps
            morning_questions = 0
            evening_questions = 0
            
            for question in questions:
                hour = question['created_at'].hour
                if 6 <= hour < 12:
                    morning_questions += 1
                elif 18 <= hour < 24:
                    evening_questions += 1
            
            if morning_questions > evening_questions:
                preferences['preferred_time'] = 'morning'
            elif evening_questions > morning_questions:
                preferences['preferred_time'] = 'evening'
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error analyzing study preferences: {e}")
            return {}
    
    async def _analyze_question_patterns(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's question patterns"""
        try:
            patterns = {
                'style': 'formal',
                'complexity': 'medium',
                'subject_focus': 'general'
            }
            
            # Analyze question style
            formal_indicators = ['لطفاً', 'ممکن است', 'آیا می‌توانید', 'خواهشمندم']
            informal_indicators = ['میشه', 'می‌تونی', 'لطفا', 'ممنون']
            
            formal_count = sum(1 for q in questions for indicator in formal_indicators if indicator in q['question_text'])
            informal_count = sum(1 for q in questions for indicator in informal_indicators if indicator in q['question_text'])
            
            if formal_count > informal_count:
                patterns['style'] = 'formal'
            elif informal_count > formal_count:
                patterns['style'] = 'informal'
            
            # Analyze question complexity
            complex_indicators = ['چرا', 'چگونه', 'چه زمانی', 'کجا', 'چطور']
            simple_indicators = ['چی', 'کیه', 'کدوم', 'کجا']
            
            complex_count = sum(1 for q in questions for indicator in complex_indicators if indicator in q['question_text'])
            simple_count = sum(1 for q in questions for indicator in simple_indicators if indicator in q['question_text'])
            
            if complex_count > simple_count:
                patterns['complexity'] = 'high'
            elif simple_count > complex_count:
                patterns['complexity'] = 'low'
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing question patterns: {e}")
            return {}
    
    async def _analyze_response_preferences(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's response preferences"""
        try:
            # Get user's feedback on answers
            query = """
                SELECT 
                    f.rating, f.is_helpful, f.feedback_text,
                    q.question_text, a.answer_text
                FROM qa_feedback f
                JOIN qa_questions q ON f.question_id = q.question_id
                JOIN qa_answers a ON f.answer_id = a.answer_id
                WHERE q.user_id = $1
                ORDER BY f.created_at DESC
                LIMIT 20
            """
            
            results = await db_manager.fetch_all(query, user_id)
            
            if not results:
                return {'preferred_length': 'medium', 'detail_level': 'moderate'}
            
            # Analyze feedback patterns
            high_rated = [r for r in results if r['rating'] >= 4]
            low_rated = [r for r in results if r['rating'] <= 2]
            
            preferences = {
                'preferred_length': 'medium',
                'detail_level': 'moderate',
                'example_preference': 'moderate'
            }
            
            # Analyze preferred answer length
            if high_rated:
                avg_length = sum(len(r['answer_text']) for r in high_rated) / len(high_rated)
                if avg_length > 1000:
                    preferences['preferred_length'] = 'long'
                elif avg_length < 500:
                    preferences['preferred_length'] = 'short'
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error analyzing response preferences: {e}")
            return {}
    
    async def _analyze_learning_goals(self, user_id: int, questions: List[Dict[str, Any]]) -> List[str]:
        """Analyze user's learning goals"""
        try:
            goals = []
            
            # Analyze goals from question patterns
            goal_keywords = {
                'کنکور': ['کنکور', 'آزمون', 'رتبه', 'دانشگاه'],
                'مشاوره تحصیلی': ['مشاوره', 'راهنمایی', 'انتخاب', 'برنامه'],
                'انگیزه': ['انگیزه', 'تشویق', 'انگیزشی', 'مثبت'],
                'مهارت‌آموزی': ['مهارت', 'یادگیری', 'آموزش', 'تمرین']
            }
            
            for goal, keywords in goal_keywords.items():
                count = sum(1 for q in questions for keyword in keywords if keyword in q['question_text'])
                if count > 0:
                    goals.append(goal)
            
            return goals
            
        except Exception as e:
            self.logger.error(f"Error analyzing learning goals: {e}")
            return []
    
    async def _analyze_strengths_weaknesses(self, user_id: int, questions: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Analyze user's strengths and weaknesses"""
        try:
            strengths = []
            weaknesses = []
            
            # Get user's study statistics
            query = """
                SELECT 
                    study_track, current_level, total_points
                FROM users u
                LEFT JOIN user_levels ul ON u.user_id = ul.user_id
                WHERE u.user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if result:
                study_track = result['study_track']
                level = result['current_level']
                points = result['total_points']
                
                # Determine strengths based on level and points
                if level >= 6:
                    strengths.append('پیشرفت تحصیلی')
                if points >= 1000:
                    strengths.append('انگیزه و پشتکار')
                
                # Determine weaknesses based on question patterns
                if len(questions) < 5:
                    weaknesses.append('فعالیت کم در پرسش و پاسخ')
                
                # Analyze question categories for weaknesses
                category_counts = {}
                for question in questions:
                    if question['category_id']:
                        category_counts[question['category_id']] = category_counts.get(question['category_id'], 0) + 1
                
                # Find least asked categories
                if category_counts:
                    min_count = min(category_counts.values())
                    weak_categories = [cat for cat, count in category_counts.items() if count == min_count]
                    if weak_categories:
                        weaknesses.append('عدم تمرکز روی برخی موضوعات')
            
            return strengths, weaknesses
            
        except Exception as e:
            self.logger.error(f"Error analyzing strengths and weaknesses: {e}")
            return [], []
    
    async def _save_learning_profile(self, profile: UserLearningProfile) -> None:
        """Save learning profile to database"""
        try:
            query = """
                INSERT INTO user_learning_profiles 
                (user_id, learning_level, interest_areas, study_preferences, 
                 question_patterns, response_preferences, learning_goals, 
                 strengths, weaknesses, last_updated)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (user_id) 
                DO UPDATE SET
                    learning_level = EXCLUDED.learning_level,
                    interest_areas = EXCLUDED.interest_areas,
                    study_preferences = EXCLUDED.study_preferences,
                    question_patterns = EXCLUDED.question_patterns,
                    response_preferences = EXCLUDED.response_preferences,
                    learning_goals = EXCLUDED.learning_goals,
                    strengths = EXCLUDED.strengths,
                    weaknesses = EXCLUDED.weaknesses,
                    last_updated = EXCLUDED.last_updated
            """
            
            await db_manager.execute(
                query,
                profile.user_id,
                profile.learning_level.value,
                [area.value for area in profile.interest_areas],
                profile.study_preferences,
                profile.question_patterns,
                profile.response_preferences,
                profile.learning_goals,
                profile.strengths,
                profile.weaknesses,
                profile.last_updated
            )
            
        except Exception as e:
            self.logger.error(f"Error saving learning profile: {e}")
    
    async def _get_learning_profile(self, user_id: int) -> Optional[UserLearningProfile]:
        """Get user learning profile"""
        try:
            query = """
                SELECT * FROM user_learning_profiles WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if not result:
                return None
            
            return UserLearningProfile(
                user_id=result['user_id'],
                learning_level=LearningLevel(result['learning_level']),
                interest_areas=[InterestArea(area) for area in result['interest_areas']],
                study_preferences=result['study_preferences'],
                question_patterns=result['question_patterns'],
                response_preferences=result['response_preferences'],
                learning_goals=result['learning_goals'],
                strengths=result['strengths'],
                weaknesses=result['weaknesses'],
                last_updated=result['last_updated']
            )
            
        except Exception as e:
            self.logger.error(f"Error getting learning profile: {e}")
            return None
    
    async def _analyze_question_context(self, question_text: str, profile: UserLearningProfile) -> Dict[str, Any]:
        """Analyze question context for personalized response"""
        try:
            context = {}
            
            # Add level-appropriate context
            if profile.learning_level == LearningLevel.BEGINNER:
                context['explanation_level'] = 'basic'
                context['use_examples'] = True
            elif profile.learning_level == LearningLevel.INTERMEDIATE:
                context['explanation_level'] = 'moderate'
                context['use_examples'] = True
            elif profile.learning_level == LearningLevel.ADVANCED:
                context['explanation_level'] = 'detailed'
                context['use_examples'] = False
            else:  # EXPERT
                context['explanation_level'] = 'expert'
                context['use_examples'] = False
            
            # Add interest-based context
            context['focus_areas'] = [area.value for area in profile.interest_areas]
            
            # Add style preferences
            context['response_style'] = profile.question_patterns.get('style', 'formal')
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error analyzing question context: {e}")
            return {}
    
    def _get_default_context(self) -> Dict[str, Any]:
        """Get default context when no profile exists"""
        return {
            'user_level': 'beginner',
            'interest_areas': [],
            'study_preferences': {},
            'learning_goals': [],
            'strengths': [],
            'weaknesses': [],
            'question_style': 'formal',
            'response_preferences': {},
            'explanation_level': 'basic',
            'use_examples': True,
            'focus_areas': [],
            'response_style': 'formal'
        }
    
    async def _generate_learning_insights(self, user_id: int, profile: UserLearningProfile) -> None:
        """Generate learning insights for user"""
        try:
            insights = []
            
            # Generate insights based on profile
            if profile.learning_level == LearningLevel.BEGINNER:
                insights.append({
                    'type': 'encouragement',
                    'title': 'شروع خوب!',
                    'description': 'شما در ابتدای مسیر یادگیری هستید. ادامه دهید!',
                    'confidence': 0.8
                })
            
            if len(profile.interest_areas) > 3:
                insights.append({
                    'type': 'diversity',
                    'title': 'تنوع علایق',
                    'description': 'شما در زمینه‌های مختلفی سوال می‌پرسید که نشان‌دهنده کنجکاوی بالای شماست.',
                    'confidence': 0.9
                })
            
            if 'کنکور' in profile.learning_goals:
                insights.append({
                    'type': 'goal_focus',
                    'title': 'تمرکز روی کنکور',
                    'description': 'اهداف شما نشان می‌دهد که روی کنکور متمرکز هستید.',
                    'confidence': 0.7
                })
            
            # Save insights
            for insight in insights:
                await self._save_learning_insight(user_id, insight)
            
        except Exception as e:
            self.logger.error(f"Error generating learning insights: {e}")
    
    async def _save_learning_insight(self, user_id: int, insight: Dict[str, Any]) -> None:
        """Save learning insight"""
        try:
            query = """
                INSERT INTO learning_insights 
                (user_id, insight_type, insight_data, confidence_score)
                VALUES ($1, $2, $3, $4)
            """
            
            await db_manager.execute(
                query,
                user_id,
                insight['type'],
                insight,
                insight['confidence']
            )
            
        except Exception as e:
            self.logger.error(f"Error saving learning insight: {e}")
    
    async def _update_learning_metrics(self, user_id: int, question_text: str, answer_quality: float) -> None:
        """Update learning metrics based on new interaction"""
        try:
            # This would update various learning metrics
            # Implementation depends on specific metrics to track
            pass
            
        except Exception as e:
            self.logger.error(f"Error updating learning metrics: {e}")
    
    async def _should_update_profile(self, user_id: int) -> bool:
        """Check if profile should be updated"""
        try:
            query = """
                SELECT last_updated FROM user_learning_profiles 
                WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if not result:
                return True
            
            last_updated = result['last_updated']
            hours_since_update = (datetime.now() - last_updated).total_seconds() / 3600
            
            return hours_since_update >= self.learning_config['update_frequency_hours']
            
        except Exception as e:
            self.logger.error(f"Error checking if profile should update: {e}")
            return False


# Global user learning service instance
user_learning_service = UserLearningService()
