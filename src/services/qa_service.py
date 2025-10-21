"""
🌌 SarlakBot v3.1.0 - Q&A Service
Advanced Q&A system with OpenAI integration and points-based access
"""

import asyncio
import json
import openai
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum

from src.database.connection import db_manager
from src.config import config
from src.utils.logging import get_logger
from src.services.user_learning_service import user_learning_service

logger = get_logger(__name__)


class QuestionStatus(Enum):
    """Question status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    ANSWERED = "answered"
    FAILED = "failed"


class QuestionPriority(Enum):
    """Question priority enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AnswerType(Enum):
    """Answer type enumeration"""
    AI = "ai"
    HUMAN = "human"
    HYBRID = "hybrid"


@dataclass
class QAQuestion:
    """Q&A question data structure"""
    question_id: int
    user_id: int
    category_id: Optional[int]
    question_text: str
    question_context: Optional[str]
    question_language: str
    points_cost: int
    status: QuestionStatus
    priority: QuestionPriority
    created_at: datetime
    updated_at: datetime


@dataclass
class QAAnswer:
    """Q&A answer data structure"""
    answer_id: int
    question_id: int
    answer_text: str
    answer_type: AnswerType
    confidence_score: float
    sources: List[str]
    follow_up_suggestions: List[str]
    is_helpful: Optional[bool]
    created_at: datetime


@dataclass
class QASession:
    """Q&A session data structure"""
    session_id: int
    user_id: int
    session_title: Optional[str]
    total_questions: int
    total_points_spent: int
    session_status: str
    started_at: datetime
    ended_at: Optional[datetime]
    last_activity: datetime


class QAService:
    """
    🌌 Q&A Service
    Advanced Q&A system with OpenAI integration
    """
    
    def __init__(self):
        self.logger = logger
        self.openai_client = None
        self._initialize_openai()
        
        # Q&A configuration
        self.qa_config = {
            'default_points_cost': 10,
            'premium_points_cost': 20,
            'urgent_points_cost': 50,
            'max_question_length': 1000,
            'max_context_length': 500,
            'max_retries': 3,
            'timeout_seconds': 30
        }
        
        # OpenAI configuration
        self.openai_config = {
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.9,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.1
        }
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            if config.ai.openai_api_key:
                openai.api_key = config.ai.openai_api_key
                self.openai_client = openai
                self.logger.info("✅ OpenAI client initialized successfully")
            else:
                self.logger.warning("⚠️ OpenAI API key not found, Q&A service will use fallback responses")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize OpenAI client: {e}")
    
    async def ask_question(
        self, 
        user_id: int, 
        question_text: str, 
        category_id: Optional[int] = None,
        question_context: Optional[str] = None,
        priority: QuestionPriority = QuestionPriority.NORMAL,
        session_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Ask a question and get AI-powered answer"""
        try:
            # Validate question
            if not self._validate_question(question_text):
                return {
                    'success': False,
                    'error': 'سوال نامعتبر است. لطفاً سوال خود را به صورت واضح و کامل بنویسید.'
                }
            
            # Calculate points cost
            points_cost = self._calculate_points_cost(priority, category_id)
            
            # Check if user has enough points
            if not await self._check_user_points(user_id, points_cost):
                return {
                    'success': False,
                    'error': f'امتیاز کافی ندارید. برای این سوال {points_cost} امتیاز نیاز است.',
                    'points_needed': points_cost
                }
            
            # Create question record
            question_id = await self._create_question(
                user_id, question_text, category_id, question_context, 
                points_cost, priority, session_id
            )
            
            if not question_id:
                return {
                    'success': False,
                    'error': 'خطا در ثبت سوال. لطفاً دوباره تلاش کنید.'
                }
            
            # Deduct points
            if not await self._deduct_points(user_id, points_cost):
                return {
                    'success': False,
                    'error': 'خطا در کسر امتیاز. لطفاً دوباره تلاش کنید.'
                }
            
            # Generate answer
            answer_result = await self._generate_answer(question_id, question_text, question_context, category_id)
            
            if answer_result['success']:
                # Update question status
                await self._update_question_status(question_id, QuestionStatus.ANSWERED)
                
                # Log analytics
                await self._log_qa_analytics(user_id, question_id, 'ask_question', points_cost)
                
                return {
                    'success': True,
                    'question_id': question_id,
                    'answer': answer_result['answer'],
                    'confidence_score': answer_result['confidence_score'],
                    'sources': answer_result['sources'],
                    'follow_up_suggestions': answer_result['follow_up_suggestions'],
                    'points_spent': points_cost
                }
            else:
                # Update question status to failed
                await self._update_question_status(question_id, QuestionStatus.FAILED)
                
                return {
                    'success': False,
                    'error': 'خطا در تولید پاسخ. امتیاز شما بازگردانده شد.',
                    'points_refunded': points_cost
                }
                
        except Exception as e:
            self.logger.error(f"Error in ask_question: {e}")
            return {
                'success': False,
                'error': 'خطای سیستم. لطفاً دوباره تلاش کنید.'
            }
    
    async def get_answer(self, question_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get answer for a specific question"""
        try:
            # Get question and answer
            query = """
                SELECT 
                    q.question_id, q.question_text, q.question_context, q.points_cost,
                    q.status, q.created_at, q.updated_at,
                    a.answer_id, a.answer_text, a.answer_type, a.confidence_score,
                    a.sources, a.follow_up_suggestions, a.created_at as answer_created_at,
                    c.category_name, c.category_icon
                FROM qa_questions q
                LEFT JOIN qa_answers a ON q.question_id = a.question_id
                LEFT JOIN qa_categories c ON q.category_id = c.category_id
                WHERE q.question_id = $1 AND q.user_id = $2
            """
            
            result = await db_manager.fetch_one(query, question_id, user_id)
            
            if not result:
                return None
            
            return {
                'question_id': result['question_id'],
                'question_text': result['question_text'],
                'question_context': result['question_context'],
                'points_cost': result['points_cost'],
                'status': result['status'],
                'created_at': result['created_at'],
                'answer': {
                    'answer_id': result['answer_id'],
                    'answer_text': result['answer_text'],
                    'answer_type': result['answer_type'],
                    'confidence_score': result['confidence_score'],
                    'sources': result['sources'] or [],
                    'follow_up_suggestions': result['follow_up_suggestions'] or [],
                    'created_at': result['answer_created_at']
                } if result['answer_id'] else None,
                'category': {
                    'name': result['category_name'],
                    'icon': result['category_icon']
                } if result['category_name'] else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting answer: {e}")
            return None
    
    async def rate_answer(self, question_id: int, user_id: int, rating: int, feedback_text: Optional[str] = None) -> bool:
        """Rate an answer"""
        try:
            if not (1 <= rating <= 5):
                return False
            
            # Check if question exists and belongs to user
            question = await db_manager.fetch_one(
                "SELECT question_id FROM qa_questions WHERE question_id = $1 AND user_id = $2",
                question_id, user_id
            )
            
            if not question:
                return False
            
            # Get answer ID
            answer = await db_manager.fetch_one(
                "SELECT answer_id FROM qa_answers WHERE question_id = $1",
                question_id
            )
            
            if not answer:
                return False
            
            # Insert or update feedback
            await db_manager.execute(
                """
                INSERT INTO qa_feedback (question_id, answer_id, user_id, rating, feedback_text, is_helpful)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (question_id, user_id) 
                DO UPDATE SET rating = $4, feedback_text = $5, is_helpful = $6, created_at = NOW()
                """,
                question_id, answer['answer_id'], user_id, rating, feedback_text, rating >= 4
            )
            
            # Log analytics
            await self._log_qa_analytics(user_id, question_id, 'rate_answer', 0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rating answer: {e}")
            return False
    
    async def get_user_qa_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get user Q&A statistics"""
        try:
            query = """
                SELECT 
                    COUNT(DISTINCT q.question_id) as total_questions,
                    COALESCE(SUM(q.points_cost), 0) as total_points_spent,
                    COALESCE(AVG(f.rating), 0.0) as avg_rating,
                    COUNT(CASE WHEN f.is_helpful = TRUE THEN 1 END) as helpful_answers,
                    COUNT(CASE WHEN q.status = 'answered' THEN 1 END) as answered_questions,
                    COUNT(CASE WHEN q.status = 'failed' THEN 1 END) as failed_questions
                FROM qa_questions q
                LEFT JOIN qa_feedback f ON q.question_id = f.question_id
                WHERE q.user_id = $1 
                AND q.created_at >= CURRENT_DATE - INTERVAL '1 day' * $2
            """
            
            result = await db_manager.fetch_one(query, user_id, days)
            
            if not result:
                return {
                    'total_questions': 0,
                    'total_points_spent': 0,
                    'avg_rating': 0.0,
                    'helpful_answers': 0,
                    'answered_questions': 0,
                    'failed_questions': 0
                }
            
            return {
                'total_questions': result['total_questions'],
                'total_points_spent': result['total_points_spent'],
                'avg_rating': round(result['avg_rating'], 2),
                'helpful_answers': result['helpful_answers'],
                'answered_questions': result['answered_questions'],
                'failed_questions': result['failed_questions']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user Q&A stats: {e}")
            return {}
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get available Q&A categories"""
        try:
            query = """
                SELECT category_id, category_name, category_description, category_icon
                FROM qa_categories
                WHERE is_active = TRUE
                ORDER BY category_name
            """
            
            results = await db_manager.fetch_all(query)
            
            categories = []
            for row in results:
                categories.append({
                    'category_id': row['category_id'],
                    'name': row['category_name'],
                    'description': row['category_description'],
                    'icon': row['category_icon']
                })
            
            return categories
            
        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            return []
    
    async def get_popular_questions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular questions"""
        try:
            query = """
                SELECT 
                    q.question_id,
                    q.question_text,
                    c.category_name,
                    c.category_icon,
                    COUNT(*) as ask_count,
                    COALESCE(AVG(f.rating), 0.0) as avg_rating
                FROM qa_questions q
                LEFT JOIN qa_categories c ON q.category_id = c.category_id
                LEFT JOIN qa_feedback f ON q.question_id = f.question_id
                WHERE q.status = 'answered'
                GROUP BY q.question_id, q.question_text, c.category_name, c.category_icon
                ORDER BY ask_count DESC, avg_rating DESC
                LIMIT $1
            """
            
            results = await db_manager.fetch_all(query, limit)
            
            questions = []
            for row in results:
                questions.append({
                    'question_id': row['question_id'],
                    'question_text': row['question_text'],
                    'category_name': row['category_name'],
                    'category_icon': row['category_icon'],
                    'ask_count': row['ask_count'],
                    'avg_rating': round(row['avg_rating'], 2)
                })
            
            return questions
            
        except Exception as e:
            self.logger.error(f"Error getting popular questions: {e}")
            return []
    
    async def create_session(self, user_id: int, session_title: Optional[str] = None) -> Optional[int]:
        """Create a new Q&A session"""
        try:
            query = """
                INSERT INTO qa_sessions (user_id, session_title, started_at, last_activity)
                VALUES ($1, $2, NOW(), NOW())
                RETURNING session_id
            """
            
            result = await db_manager.fetch_one(query, user_id, session_title)
            return result['session_id'] if result else None
            
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            return None
    
    async def get_user_sessions(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's Q&A sessions"""
        try:
            query = """
                SELECT 
                    session_id, session_title, total_questions, total_points_spent,
                    session_status, started_at, ended_at, last_activity
                FROM qa_sessions
                WHERE user_id = $1
                ORDER BY started_at DESC
                LIMIT $2
            """
            
            results = await db_manager.fetch_all(query, user_id, limit)
            
            sessions = []
            for row in results:
                sessions.append({
                    'session_id': row['session_id'],
                    'title': row['session_title'],
                    'total_questions': row['total_questions'],
                    'total_points_spent': row['total_points_spent'],
                    'status': row['session_status'],
                    'started_at': row['started_at'],
                    'ended_at': row['ended_at'],
                    'last_activity': row['last_activity']
                })
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error getting user sessions: {e}")
            return []
    
    def _validate_question(self, question_text: str) -> bool:
        """Validate question text"""
        if not question_text or len(question_text.strip()) < 10:
            return False
        
        if len(question_text) > self.qa_config['max_question_length']:
            return False
        
        # Check for inappropriate content (basic check)
        inappropriate_words = ['spam', 'test', 'تست', 'اسپم']
        question_lower = question_text.lower()
        
        for word in inappropriate_words:
            if word in question_lower and len(question_text) < 50:
                return False
        
        return True
    
    def _calculate_points_cost(self, priority: QuestionPriority, category_id: Optional[int]) -> int:
        """Calculate points cost for a question"""
        base_cost = self.qa_config['default_points_cost']
        
        if priority == QuestionPriority.URGENT:
            return self.qa_config['urgent_points_cost']
        elif priority == QuestionPriority.HIGH:
            return int(base_cost * 1.5)
        elif priority == QuestionPriority.LOW:
            return int(base_cost * 0.5)
        
        # Premium categories cost more
        if category_id in [11, 12, 13]:  # مشاوره تحصیلی, کنکور, انگیزشی
            return self.qa_config['premium_points_cost']
        
        return base_cost
    
    async def _check_user_points(self, user_id: int, points_cost: int) -> bool:
        """Check if user has enough points"""
        try:
            query = """
                SELECT total_points FROM user_levels WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            user_points = result['total_points'] if result else 0
            
            return user_points >= points_cost
            
        except Exception as e:
            self.logger.error(f"Error checking user points: {e}")
            return False
    
    async def _deduct_points(self, user_id: int, points: int) -> bool:
        """Deduct points from user"""
        try:
            query = """
                UPDATE user_levels 
                SET total_points = total_points - $2
                WHERE user_id = $1 AND total_points >= $2
            """
            
            result = await db_manager.execute(query, user_id, points)
            return result is not None
            
        except Exception as e:
            self.logger.error(f"Error deducting points: {e}")
            return False
    
    async def _create_question(
        self, 
        user_id: int, 
        question_text: str, 
        category_id: Optional[int],
        question_context: Optional[str],
        points_cost: int,
        priority: QuestionPriority,
        session_id: Optional[int]
    ) -> Optional[int]:
        """Create question record"""
        try:
            query = """
                INSERT INTO qa_questions 
                (user_id, category_id, question_text, question_context, points_cost, status, priority)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING question_id
            """
            
            result = await db_manager.fetch_one(
                query, user_id, category_id, question_text, 
                question_context, points_cost, priority.value, priority.value
            )
            
            return result['question_id'] if result else None
            
        except Exception as e:
            self.logger.error(f"Error creating question: {e}")
            return None
    
    async def _generate_answer(
        self, 
        question_id: int, 
        question_text: str, 
        question_context: Optional[str],
        category_id: Optional[int]
    ) -> Dict[str, Any]:
        """Generate AI-powered answer with user personalization"""
        try:
            # Update question status to processing
            await self._update_question_status(question_id, QuestionStatus.PROCESSING)
            
            # Get user ID from question
            question_data = await db_manager.fetch_one(
                "SELECT user_id FROM qa_questions WHERE question_id = $1",
                question_id
            )
            user_id = question_data['user_id'] if question_data else None
            
            # Get personalized context for user
            personalized_context = {}
            if user_id:
                personalized_context = await user_learning_service.get_personalized_response_context(
                    user_id, question_text
                )
            
            # Get category info for context
            category_info = ""
            if category_id:
                category = await db_manager.fetch_one(
                    "SELECT category_name, category_description FROM qa_categories WHERE category_id = $1",
                    category_id
                )
                if category:
                    category_info = f"دسته‌بندی: {category['category_name']}\nتوضیحات: {category['category_description']}\n\n"
            
            # Prepare personalized prompt
            prompt = self._prepare_personalized_prompt(
                question_text, question_context, category_info, personalized_context
            )
            
            # Generate answer using OpenAI
            if self.openai_client:
                answer_result = await self._call_openai(prompt)
            else:
                answer_result = self._get_fallback_answer(question_text, category_id)
            
            if answer_result['success']:
                # Save answer to database
                answer_id = await self._save_answer(
                    question_id, answer_result['answer'], answer_result['confidence_score'],
                    answer_result['sources'], answer_result['follow_up_suggestions']
                )
                
                if answer_id:
                    # Track learning progress
                    if user_id:
                        await user_learning_service.track_learning_progress(
                            user_id, question_text, answer_result['confidence_score']
                        )
                    
                    return {
                        'success': True,
                        'answer': answer_result['answer'],
                        'confidence_score': answer_result['confidence_score'],
                        'sources': answer_result['sources'],
                        'follow_up_suggestions': answer_result['follow_up_suggestions']
                    }
            
            return {'success': False, 'error': 'Failed to generate answer'}
            
        except Exception as e:
            self.logger.error(f"Error generating answer: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_prompt(self, question_text: str, question_context: Optional[str], category_info: str) -> str:
        """Prepare prompt for OpenAI"""
        base_prompt = f"""
شما یک دستیار هوشمند آموزشی برای دانش‌آموزان کنکوری هستید. لطفاً به سوال زیر پاسخ دهید:

{category_info}سوال: {question_text}

{question_context if question_context else ""}

لطفاً پاسخ خود را به صورت:
1. کامل و دقیق
2. قابل فهم برای دانش‌آموز
3. با مثال‌های عملی
4. با منابع معتبر
5. به زبان فارسی

ارائه دهید.
"""
        return base_prompt.strip()
    
    def _prepare_personalized_prompt(
        self, 
        question_text: str, 
        question_context: Optional[str], 
        category_info: str,
        personalized_context: Dict[str, Any]
    ) -> str:
        """Prepare personalized prompt for OpenAI based on user learning profile"""
        try:
            # Build personalized context
            user_level = personalized_context.get('user_level', 'beginner')
            interest_areas = personalized_context.get('interest_areas', [])
            learning_goals = personalized_context.get('learning_goals', [])
            strengths = personalized_context.get('strengths', [])
            weaknesses = personalized_context.get('weaknesses', [])
            explanation_level = personalized_context.get('explanation_level', 'basic')
            use_examples = personalized_context.get('use_examples', True)
            response_style = personalized_context.get('response_style', 'formal')
            
            # Build context string
            context_parts = []
            
            if user_level != 'beginner':
                context_parts.append(f"سطح کاربر: {user_level}")
            
            if interest_areas:
                context_parts.append(f"علایق: {', '.join(interest_areas)}")
            
            if learning_goals:
                context_parts.append(f"اهداف: {', '.join(learning_goals)}")
            
            if strengths:
                context_parts.append(f"نقاط قوت: {', '.join(strengths)}")
            
            if weaknesses:
                context_parts.append(f"نقاط ضعف: {', '.join(weaknesses)}")
            
            context_string = "\n".join(context_parts)
            
            # Build personalized prompt
            personalized_prompt = f"""
شما یک دستیار هوشمند آموزشی برای دانش‌آموزان کنکوری هستید. لطفاً به سوال زیر پاسخ دهید:

{category_info}سوال: {question_text}

{question_context if question_context else ""}

**اطلاعات شخصی‌سازی شده کاربر:**
{context_string}

**دستورالعمل‌های پاسخ‌دهی:**
- سطح توضیح: {explanation_level}
- استفاده از مثال: {'بله' if use_examples else 'خیر'}
- سبک پاسخ: {response_style}
- توجه به نقاط قوت و ضعف کاربر
- تطبیق با اهداف یادگیری کاربر

لطفاً پاسخ خود را به صورت:
1. کامل و دقیق
2. قابل فهم برای دانش‌آموز
3. {'با مثال‌های عملی' if use_examples else 'بدون مثال‌های اضافی'}
4. با منابع معتبر
5. به زبان فارسی
6. شخصی‌سازی شده بر اساس پروفایل کاربر

ارائه دهید.
"""
            return personalized_prompt.strip()
            
        except Exception as e:
            self.logger.error(f"Error preparing personalized prompt: {e}")
            # Fallback to basic prompt
            return self._prepare_prompt(question_text, question_context, category_info)
    
    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            response = await asyncio.wait_for(
                self.openai_client.ChatCompletion.acreate(
                    model=self.openai_config['model'],
                    messages=[
                        {
                            "role": "system",
                            "content": "شما یک دستیار هوشمند آموزشی برای دانش‌آموزان کنکوری هستید. پاسخ‌های شما باید کامل، دقیق و قابل فهم باشد."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=self.openai_config['temperature'],
                    max_tokens=self.openai_config['max_tokens'],
                    top_p=self.openai_config['top_p'],
                    frequency_penalty=self.openai_config['frequency_penalty'],
                    presence_penalty=self.openai_config['presence_penalty']
                ),
                timeout=self.qa_config['timeout_seconds']
            )
            
            answer_text = response.choices[0].message.content.strip()
            
            # Extract sources and follow-up suggestions
            sources = self._extract_sources(answer_text)
            follow_up_suggestions = self._generate_follow_up_suggestions(answer_text)
            
            return {
                'success': True,
                'answer': answer_text,
                'confidence_score': 0.9,  # High confidence for GPT-4
                'sources': sources,
                'follow_up_suggestions': follow_up_suggestions
            }
            
        except asyncio.TimeoutError:
            self.logger.error("OpenAI API timeout")
            return {'success': False, 'error': 'API timeout'}
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_fallback_answer(self, question_text: str, category_id: Optional[int]) -> Dict[str, Any]:
        """Get fallback answer when OpenAI is not available"""
        fallback_responses = {
            1: "سوال ریاضی شما دریافت شد. برای پاسخ دقیق، لطفاً با مشاور تحصیلی تماس بگیرید.",
            2: "سوال فیزیک شما دریافت شد. برای پاسخ دقیق، لطفاً با مشاور تحصیلی تماس بگیرید.",
            3: "سوال شیمی شما دریافت شد. برای پاسخ دقیق، لطفاً با مشاور تحصیلی تماس بگیرید.",
            11: "سوال مشاوره تحصیلی شما دریافت شد. برای راهنمایی کامل، لطفاً با مشاور تماس بگیرید.",
            12: "سوال کنکور شما دریافت شد. برای پاسخ دقیق، لطفاً با مشاور تحصیلی تماس بگیرید.",
            13: "سوال انگیزشی شما دریافت شد. برای راهنمایی کامل، لطفاً با مشاور تماس بگیرید."
        }
        
        answer = fallback_responses.get(category_id, "سوال شما دریافت شد. برای پاسخ دقیق، لطفاً با مشاور تحصیلی تماس بگیرید.")
        
        return {
            'success': True,
            'answer': answer,
            'confidence_score': 0.3,  # Low confidence for fallback
            'sources': [],
            'follow_up_suggestions': [
                "آیا سوال دیگری دارید؟",
                "آیا نیاز به توضیح بیشتری دارید؟",
                "آیا می‌خواهید با مشاور صحبت کنید؟"
            ]
        }
    
    def _extract_sources(self, answer_text: str) -> List[str]:
        """Extract sources from answer text"""
        # Simple source extraction (can be improved)
        sources = []
        
        # Look for common source patterns
        if "منبع" in answer_text or "مرجع" in answer_text:
            sources.append("منابع آموزشی آکادمی سرلک")
        
        if "کتاب" in answer_text:
            sources.append("کتاب‌های درسی")
        
        if "سایت" in answer_text or "وب‌سایت" in answer_text:
            sources.append("وب‌سایت‌های آموزشی")
        
        if not sources:
            sources.append("دانش عمومی و تجربه آموزشی")
        
        return sources
    
    def _generate_follow_up_suggestions(self, answer_text: str) -> List[str]:
        """Generate follow-up suggestions based on answer"""
        suggestions = [
            "آیا این پاسخ مفید بود؟",
            "آیا سوال دیگری دارید؟",
            "آیا نیاز به توضیح بیشتری دارید؟"
        ]
        
        # Add specific suggestions based on content
        if "ریاضی" in answer_text:
            suggestions.append("آیا می‌خواهید مثال‌های بیشتری ببینید؟")
        
        if "کنکور" in answer_text:
            suggestions.append("آیا می‌خواهید درباره استراتژی‌های کنکور بدانید؟")
        
        if "مشاوره" in answer_text:
            suggestions.append("آیا می‌خواهید با مشاور تحصیلی صحبت کنید؟")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def _save_answer(
        self, 
        question_id: int, 
        answer_text: str, 
        confidence_score: float,
        sources: List[str],
        follow_up_suggestions: List[str]
    ) -> Optional[int]:
        """Save answer to database"""
        try:
            query = """
                INSERT INTO qa_answers 
                (question_id, answer_text, answer_type, confidence_score, sources, follow_up_suggestions)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING answer_id
            """
            
            result = await db_manager.fetch_one(
                query, question_id, answer_text, AnswerType.AI.value, 
                confidence_score, sources, follow_up_suggestions
            )
            
            return result['answer_id'] if result else None
            
        except Exception as e:
            self.logger.error(f"Error saving answer: {e}")
            return None
    
    async def _update_question_status(self, question_id: int, status: QuestionStatus) -> bool:
        """Update question status"""
        try:
            query = """
                UPDATE qa_questions 
                SET status = $2, updated_at = NOW()
                WHERE question_id = $1
            """
            
            await db_manager.execute(query, question_id, status.value)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating question status: {e}")
            return False
    
    async def _log_qa_analytics(self, user_id: int, question_id: int, action_type: str, points_spent: int) -> None:
        """Log Q&A analytics"""
        try:
            query = """
                INSERT INTO qa_analytics (user_id, question_id, action_type, points_spent)
                VALUES ($1, $2, $3, $4)
            """
            
            await db_manager.execute(query, user_id, question_id, action_type, points_spent)
            
        except Exception as e:
            self.logger.error(f"Error logging Q&A analytics: {e}")


# Global Q&A service instance
qa_service = QAService()
