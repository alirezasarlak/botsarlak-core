"""
🌌 SarlakBot v3.1.0 - Q&A Handler
Intelligent Q&A system with user learning and personalization
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters

from src.services.qa_service import qa_service, QuestionPriority
from src.services.profile_service import profile_service
from src.core.security_audit import security_auditor, ActionType, SecurityLevel, AuditLog
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Conversation states
ASKING_QUESTION, SELECTING_CATEGORY, ADDING_CONTEXT, RATING_ANSWER = range(4)


class QAHandler:
    """
    🌌 Q&A Handler
    Intelligent Q&A system with user learning and personalization
    """
    
    def __init__(self):
        self.logger = logger
        self.user_contexts = {}  # Store user context for better responses
    
    async def register(self, application) -> None:
        """Register Q&A handlers"""
        try:
            from telegram.ext import CommandHandler
            
            # Register commands
            application.add_handler(CommandHandler("ask", self.ask_command))
            application.add_handler(CommandHandler("question", self.ask_command))
            application.add_handler(CommandHandler("qa", self.qa_command))
            
            # Register conversation handler for asking questions
            application.add_handler(ConversationHandler(
                entry_points=[
                    CallbackQueryHandler(self.start_ask_question, pattern="^qa_ask$"),
                    CallbackQueryHandler(self.start_ask_question, pattern="^menu_qa$")
                ],
                states={
                    ASKING_QUESTION: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_question_text),
                        CallbackQueryHandler(self.handle_category_selection, pattern="^qa_category_"),
                        CallbackQueryHandler(self.handle_priority_selection, pattern="^qa_priority_"),
                        CallbackQueryHandler(self.cancel_question, pattern="^qa_cancel$")
                    ],
                    SELECTING_CATEGORY: [
                        CallbackQueryHandler(self.handle_category_selection, pattern="^qa_category_"),
                        CallbackQueryHandler(self.skip_category, pattern="^qa_skip_category$")
                    ],
                    ADDING_CONTEXT: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_context_text),
                        CallbackQueryHandler(self.skip_context, pattern="^qa_skip_context$")
                    ],
                    RATING_ANSWER: [
                        CallbackQueryHandler(self.handle_answer_rating, pattern="^qa_rate_"),
                        CallbackQueryHandler(self.skip_rating, pattern="^qa_skip_rating$")
                    ]
                },
                fallbacks=[
                    CallbackQueryHandler(self.cancel_question, pattern="^qa_cancel$")
                ]
            ))
            
            # Register other Q&A callbacks
            application.add_handler(CallbackQueryHandler(self.show_qa_menu, pattern="^qa_menu$"))
            application.add_handler(CallbackQueryHandler(self.show_qa_history, pattern="^qa_history$"))
            application.add_handler(CallbackQueryHandler(self.show_qa_stats, pattern="^qa_stats$"))
            application.add_handler(CallbackQueryHandler(self.show_categories, pattern="^qa_categories$"))
            application.add_handler(CallbackQueryHandler(self.show_popular_questions, pattern="^qa_popular$"))
            application.add_handler(CallbackQueryHandler(self.show_answer, pattern="^qa_answer_"))
            
            self.logger.info("✅ Q&A Handler registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Q&A Handler registration failed: {e}")
            raise
    
    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /ask command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Log command usage
            await security_auditor.log_audit_event(
                AuditLog(
                    user_id=user_id,
                    action=ActionType.ROUTE_ACCESS,
                    resource="ask_command",
                    details={"command": "ask"},
                    security_level=SecurityLevel.INFO
                )
            )
            
            await self.start_ask_question(update, context)
            
        except Exception as e:
            self.logger.error(f"Ask command failed: {e}")
            await update.message.reply_text("❌ خطا در شروع سیستم پرسش و پاسخ")
    
    async def qa_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /qa command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            await self.show_qa_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"QA command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش منوی پرسش و پاسخ")
    
    async def start_ask_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start asking a question"""
        try:
            query = update.callback_query
            if query:
                await query.answer()
            
            user_id = update.effective_user.id
            
            # Get user profile for personalization
            profile = await profile_service.get_profile(user_id)
            user_name = profile.display_name if profile else update.effective_user.first_name or "عزیز"
            
            # Get user's study track for context
            study_track = profile.study_track if profile else "عمومی"
            
            # Personalized welcome message
            welcome_text = f"""
🤖 **سلام {user_name}!** 

من دستیار هوشمند آکادمی سرلک هستم و اینجا هستم تا به سوالاتت پاسخ بدم! ✨

**چیزی که من می‌دونم درباره‌ت:**
• رشته تحصیلی: {study_track}
• سطح: {profile.current_level if profile else 1}
• امتیاز: {profile.total_points if profile else 0:,}

**چطور می‌تونم کمکت کنم؟**
• سوالات درسی و کنکوری
• مشاوره تحصیلی
• راهنمایی انگیزشی
• پاسخ به هر سوال دیگه‌ای

**سوالت رو بپرس!** 🚀
"""
            
            keyboard = [
                [InlineKeyboardButton("📝 پرسیدن سوال", callback_data="qa_ask_now")],
                [InlineKeyboardButton("📚 دسته‌بندی‌ها", callback_data="qa_categories")],
                [InlineKeyboardButton("🔥 سوالات محبوب", callback_data="qa_popular")],
                [InlineKeyboardButton("📊 آمار من", callback_data="qa_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if query:
                await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
            
            return ASKING_QUESTION
            
        except Exception as e:
            self.logger.error(f"Start ask question failed: {e}")
            return ConversationHandler.END
    
    async def handle_question_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle question text input"""
        try:
            user_id = update.effective_user.id
            question_text = update.message.text.strip()
            
            # Store question in context
            context.user_data['question_text'] = question_text
            
            # Analyze question for better categorization
            suggested_category = await self._analyze_question_category(question_text, user_id)
            
            # Show category selection
            categories = await qa_service.get_categories()
            
            text = f"""
📝 **سوال شما:**
"{question_text}"

**دسته‌بندی پیشنهادی:** {suggested_category['name'] if suggested_category else 'عمومی'}

لطفاً دسته‌بندی مناسب را انتخاب کنید:
"""
            
            keyboard = []
            for category in categories[:8]:  # Show first 8 categories
                keyboard.append([
                    InlineKeyboardButton(
                        f"{category['icon']} {category['name']}", 
                        callback_data=f"qa_category_{category['category_id']}"
                    )
                ])
            
            keyboard.extend([
                [InlineKeyboardButton("⏭️ رد کردن دسته‌بندی", callback_data="qa_skip_category")],
                [InlineKeyboardButton("❌ لغو", callback_data="qa_cancel")]
            ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
            return SELECTING_CATEGORY
            
        except Exception as e:
            self.logger.error(f"Handle question text failed: {e}")
            return ConversationHandler.END
    
    async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle category selection"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            category_id = int(query.data.split('_')[-1])
            
            # Store category in context
            context.user_data['category_id'] = category_id
            
            # Get category info
            categories = await qa_service.get_categories()
            selected_category = next((c for c in categories if c['category_id'] == category_id), None)
            
            text = f"""
✅ **دسته‌بندی انتخاب شد:** {selected_category['name'] if selected_category else 'نامشخص'}

حالا می‌تونی توضیحات اضافی یا زمینه سوالت رو اضافه کنی (اختیاری):

**مثال:**
• "این سوال مربوط به کنکور 1404 هست"
• "من پایه دوازدهم هستم"
• "این سوال رو در آزمون آزمایشی دیدم"
"""
            
            keyboard = [
                [InlineKeyboardButton("⏭️ رد کردن توضیحات", callback_data="qa_skip_context")],
                [InlineKeyboardButton("❌ لغو", callback_data="qa_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
            return ADDING_CONTEXT
            
        except Exception as e:
            self.logger.error(f"Handle category selection failed: {e}")
            return ConversationHandler.END
    
    async def handle_priority_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle priority selection"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            priority_str = query.data.split('_')[-1]  # urgent, high, normal
            
            # Map priority string to enum
            priority_map = {
                'urgent': QuestionPriority.URGENT,
                'high': QuestionPriority.HIGH,
                'normal': QuestionPriority.NORMAL
            }
            
            priority = priority_map.get(priority_str, QuestionPriority.NORMAL)
            
            # Store priority in context
            context.user_data['priority'] = priority
            
            text = f"""
✅ **اولویت انتخاب شد:** {priority_str.upper()}

حالا می‌تونی توضیحات اضافی یا زمینه سوالت رو اضافه کنی (اختیاری):

**مثال:**
• "این سوال مربوط به کنکور 1404 هست"
• "من پایه دوازدهم هستم"
• "این سوال رو در آزمون آزمایشی دیدم"
"""
            
            keyboard = [
                [InlineKeyboardButton("⏭️ رد کردن توضیحات", callback_data="qa_skip_context")],
                [InlineKeyboardButton("❌ لغو", callback_data="qa_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
            return ADDING_CONTEXT
            
        except Exception as e:
            self.logger.error(f"Handle priority selection failed: {e}")
            return ConversationHandler.END
    
    async def skip_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skip category selection"""
        try:
            query = update.callback_query
            await query.answer()
            
            context.user_data['category_id'] = None
            
            text = """
📝 **سوال شما بدون دسته‌بندی ثبت می‌شود**

حالا می‌تونی توضیحات اضافی یا زمینه سوالت رو اضافه کنی (اختیاری):
"""
            
            keyboard = [
                [InlineKeyboardButton("⏭️ رد کردن توضیحات", callback_data="qa_skip_context")],
                [InlineKeyboardButton("❌ لغو", callback_data="qa_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
            return ADDING_CONTEXT
            
        except Exception as e:
            self.logger.error(f"Skip category failed: {e}")
            return ConversationHandler.END
    
    async def handle_context_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle context text input"""
        try:
            user_id = update.effective_user.id
            context_text = update.message.text.strip()
            
            # Store context in context
            context.user_data['question_context'] = context_text
            
            await self._process_question(update, context)
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Handle context text failed: {e}")
            return ConversationHandler.END
    
    async def skip_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skip context input"""
        try:
            query = update.callback_query
            await query.answer()
            
            context.user_data['question_context'] = None
            
            await self._process_question(update, context)
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Skip context failed: {e}")
            return ConversationHandler.END
    
    async def _process_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process the complete question"""
        try:
            user_id = update.effective_user.id
            question_text = context.user_data.get('question_text')
            category_id = context.user_data.get('category_id')
            question_context = context.user_data.get('question_context')
            
            # Show processing message
            processing_msg = await update.message.reply_text(
                "🤖 **در حال پردازش سوال شما...**\n\n"
                "لطفاً صبر کنید، هوش مصنوعی در حال تحلیل و پاسخ‌دهی است...",
                parse_mode='Markdown'
            )
            
            # Ask the question
            result = await qa_service.ask_question(
                user_id=user_id,
                question_text=question_text,
                category_id=category_id,
                question_context=question_context,
                priority=QuestionPriority.NORMAL
            )
            
            if result['success']:
                # Show answer
                await self._show_answer(update, result, processing_msg)
            else:
                # Show error
                await processing_msg.edit_text(
                    f"❌ **خطا در پردازش سوال:**\n\n{result.get('error', 'خطای نامشخص')}",
                    parse_mode='Markdown'
                )
            
        except Exception as e:
            self.logger.error(f"Process question failed: {e}")
            await update.message.reply_text("❌ خطا در پردازش سوال")
    
    async def _show_answer(self, update: Update, result: Dict[str, Any], processing_msg) -> None:
        """Show the answer to user"""
        try:
            answer = result['answer']
            confidence_score = result['confidence_score']
            sources = result['sources']
            follow_up_suggestions = result['follow_up_suggestions']
            points_spent = result['points_spent']
            
            # Format confidence score
            confidence_text = "عالی" if confidence_score > 0.8 else "خوب" if confidence_score > 0.6 else "متوسط"
            
            # Format answer text
            answer_text = f"""
🤖 **پاسخ هوش مصنوعی:**

{answer}

**اطلاعات پاسخ:**
• کیفیت: {confidence_text} ({confidence_score:.0%})
• امتیاز مصرف شده: {points_spent}
• منابع: {', '.join(sources) if sources else 'منابع عمومی'}
"""
            
            # Create keyboard
            keyboard = []
            
            # Follow-up suggestions
            if follow_up_suggestions:
                for i, suggestion in enumerate(follow_up_suggestions[:3]):
                    keyboard.append([
                        InlineKeyboardButton(
                            f"💬 {suggestion}", 
                            callback_data=f"qa_followup_{i}"
                        )
                    ])
            
            # Rating buttons
            keyboard.extend([
                [
                    InlineKeyboardButton("⭐ عالی", callback_data="qa_rate_5"),
                    InlineKeyboardButton("👍 خوب", callback_data="qa_rate_4"),
                    InlineKeyboardButton("👌 متوسط", callback_data="qa_rate_3")
                ],
                [
                    InlineKeyboardButton("👎 ضعیف", callback_data="qa_rate_2"),
                    InlineKeyboardButton("❌ بد", callback_data="qa_rate_1")
                ],
                [
                    InlineKeyboardButton("🔄 سوال جدید", callback_data="qa_ask"),
                    InlineKeyboardButton("📊 آمار من", callback_data="qa_stats")
                ]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(
                answer_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Show answer failed: {e}")
            await processing_msg.edit_text("❌ خطا در نمایش پاسخ")
    
    async def handle_answer_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle answer rating"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            rating = int(query.data.split('_')[-1])
            
            # Get the last question ID for this user (simplified)
            # In production, you'd store question_id in context
            question_id = context.user_data.get('last_question_id')
            
            if question_id:
                success = await qa_service.rate_answer(question_id, user_id, rating)
                
                if success:
                    await query.edit_message_text(
                        f"✅ **امتیاز {rating} ستاره ثبت شد!**\n\n"
                        "از بازخورد شما متشکرم. این کمک می‌کند تا پاسخ‌های بهتری ارائه دهم.",
                        parse_mode='Markdown'
                    )
                else:
                    await query.answer("❌ خطا در ثبت امتیاز")
            else:
                await query.answer("❌ سوال یافت نشد")
            
        except Exception as e:
            self.logger.error(f"Handle answer rating failed: {e}")
            await query.answer("❌ خطا در ثبت امتیاز")
    
    async def skip_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Skip rating"""
        try:
            query = update.callback_query
            await query.answer()
            
            await query.edit_message_text(
                "✅ **پاسخ ارائه شد!**\n\n"
                "اگر سوال دیگری دارید، می‌توانید بپرسید.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Skip rating failed: {e}")
    
    async def cancel_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel asking question"""
        try:
            query = update.callback_query
            if query:
                await query.answer()
            
            if query:
                await query.edit_message_text(
                    "❌ **پرسش لغو شد**\n\n"
                    "هر وقت آماده بودید، می‌توانید سوال جدیدی بپرسید.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ **پرسش لغو شد**\n\n"
                    "هر وقت آماده بودید، می‌توانید سوال جدیدی بپرسید.",
                    parse_mode='Markdown'
                )
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Cancel question failed: {e}")
            return ConversationHandler.END
    
    async def show_qa_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show Q&A menu"""
        try:
            query = update.callback_query
            if query:
                await query.answer()
            
            user_id = update.effective_user.id
            
            # Get user stats
            stats = await qa_service.get_user_qa_stats(user_id)
            
            text = f"""
🤖 **مرکز پرسش و پاسخ هوشمند**

**آمار شما:**
• سوالات پرسیده: {stats['total_questions']}
• امتیاز مصرف شده: {stats['total_points_spent']}
• میانگین امتیاز: {stats['avg_rating']}/5
• پاسخ‌های مفید: {stats['helpful_answers']}

**چه کاری می‌تونم برات انجام بدم؟**
"""
            
            keyboard = [
                [InlineKeyboardButton("❓ پرسیدن سوال", callback_data="qa_ask")],
                [InlineKeyboardButton("📚 دسته‌بندی‌ها", callback_data="qa_categories")],
                [InlineKeyboardButton("🔥 سوالات محبوب", callback_data="qa_popular")],
                [InlineKeyboardButton("📊 آمار کامل", callback_data="qa_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if query:
                await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Show QA menu failed: {e}")
    
    async def show_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show Q&A categories"""
        try:
            query = update.callback_query
            await query.answer()
            
            categories = await qa_service.get_categories()
            
            text = "📚 **دسته‌بندی‌های پرسش و پاسخ:**\n\n"
            
            keyboard = []
            for i in range(0, len(categories), 2):
                row = []
                for j in range(2):
                    if i + j < len(categories):
                        category = categories[i + j]
                        row.append(
                            InlineKeyboardButton(
                                f"{category['icon']} {category['name']}",
                                callback_data=f"qa_category_{category['category_id']}"
                            )
                        )
                keyboard.append(row)
            
            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="qa_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Show categories failed: {e}")
    
    async def show_popular_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show popular questions"""
        try:
            query = update.callback_query
            await query.answer()
            
            popular_questions = await qa_service.get_popular_questions(10)
            
            text = "🔥 **سوالات محبوب:**\n\n"
            
            for i, question in enumerate(popular_questions[:5], 1):
                text += f"{i}. {question['question_text'][:100]}...\n"
                text += f"   {question['category_icon']} {question['category_name']} | "
                text += f"⭐ {question['avg_rating']} | "
                text += f"👥 {question['ask_count']} بار\n\n"
            
            keyboard = [
                [InlineKeyboardButton("❓ پرسیدن سوال", callback_data="qa_ask")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="qa_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Show popular questions failed: {e}")
    
    async def show_qa_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show detailed Q&A statistics"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            stats = await qa_service.get_user_qa_stats(user_id, 30)
            
            text = f"""
📊 **آمار پرسش و پاسخ شما (30 روز گذشته):**

**📈 فعالیت:**
• سوالات پرسیده: {stats['total_questions']}
• سوالات پاسخ داده شده: {stats['answered_questions']}
• سوالات ناموفق: {stats['failed_questions']}

**💰 امتیازات:**
• امتیاز مصرف شده: {stats['total_points_spent']}
• میانگین امتیاز پاسخ‌ها: {stats['avg_rating']}/5

**👍 بازخورد:**
• پاسخ‌های مفید: {stats['helpful_answers']}
• درصد موفقیت: {(stats['answered_questions'] / max(stats['total_questions'], 1) * 100):.1f}%
"""
            
            keyboard = [
                [InlineKeyboardButton("❓ سوال جدید", callback_data="qa_ask")],
                [InlineKeyboardButton("📚 دسته‌بندی‌ها", callback_data="qa_categories")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="qa_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Show QA stats failed: {e}")
    
    async def show_qa_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show Q&A history"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            # Get user's Q&A history
            history = await qa_service.get_user_qa_history(user_id, limit=10)
            
            if not history:
                text = "📚 **تاریخچه پرسش و پاسخ شما خالی است**\n\nهنوز سوالی نپرسیده‌اید. برای شروع، روی 'پرسیدن سوال' کلیک کنید."
            else:
                text = "📚 **تاریخچه پرسش و پاسخ شما**\n\n"
                for i, item in enumerate(history, 1):
                    status_icon = "✅" if item['status'] == 'answered' else "⏳"
                    text += f"{i}. {status_icon} {item['question_text'][:50]}...\n"
                    if item['created_at']:
                        text += f"   📅 {item['created_at'].strftime('%Y/%m/%d %H:%M')}\n"
                    text += "\n"
            
            keyboard = [
                [InlineKeyboardButton("❓ پرسیدن سوال جدید", callback_data="qa_ask")],
                [InlineKeyboardButton("🏠 خانه", callback_data="go_home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Show Q&A history failed: {e}")
            await query.edit_message_text("❌ خطا در نمایش تاریخچه. لطفاً دوباره تلاش کن.")
    
    async def show_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show answer details"""
        try:
            query = update.callback_query
            await query.answer()
            
            answer_id = int(query.data.split('_')[-1])
            
            # Get answer details
            answer = await qa_service.get_answer_by_id(answer_id)
            if not answer:
                await query.edit_message_text("❌ پاسخ یافت نشد.")
                return
            
            text = f"""
🤖 **پاسخ هوشمند:**

{answer['answer_text']}

**📊 اطلاعات پاسخ:**
• اعتماد: {answer.get('confidence_score', 'نامشخص')}/10
• منابع: {answer.get('sources', 'ندارد')}
• تاریخ: {answer.get('created_at', 'نامشخص')}
"""
            
            keyboard = [
                [InlineKeyboardButton("⭐ امتیازدهی", callback_data=f"qa_rate_{answer_id}")],
                [InlineKeyboardButton("👍 مفید بود", callback_data=f"qa_helpful_{answer_id}")],
                [InlineKeyboardButton("👎 مفید نبود", callback_data=f"qa_not_helpful_{answer_id}")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="qa_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Show answer failed: {e}")
            await query.edit_message_text("❌ خطا در نمایش پاسخ. لطفاً دوباره تلاش کن.")
    
    async def _analyze_question_category(self, question_text: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Analyze question to suggest category"""
        try:
            # Simple keyword-based category suggestion
            question_lower = question_text.lower()
            
            category_keywords = {
                1: ['ریاضی', 'محاسبه', 'حل', 'فرمول', 'معادله', 'جبر', 'هندسه'],
                2: ['فیزیک', 'نیرو', 'حرکت', 'انرژی', 'مکانیک', 'الکتریسیته'],
                3: ['شیمی', 'واکنش', 'ترکیب', 'مولکول', 'اتم', 'جدول تناوبی'],
                4: ['زیست', 'سلول', 'ژن', 'تکامل', 'گیاه', 'حیوان'],
                5: ['ادبیات', 'شعر', 'نثر', 'داستان', 'نویسنده', 'شاعر'],
                6: ['تاریخ', 'تاریخی', 'دوره', 'دودمان', 'جنگ', 'انقلاب'],
                7: ['جغرافیا', 'کشور', 'شهر', 'آب و هوا', 'نقشه', 'اقلیم'],
                8: ['انگلیسی', 'grammar', 'vocabulary', 'تلفظ', 'زبان'],
                9: ['دین', 'مذهبی', 'اخلاق', 'احکام', 'قرآن', 'حدیث'],
                10: ['روانشناسی', 'ذهن', 'رفتار', 'شخصیت', 'روان'],
                11: ['مشاوره', 'راهنمایی', 'انتخاب', 'برنامه', 'مشاور'],
                12: ['کنکور', 'آزمون', 'تست', 'سوال', 'پاسخ'],
                13: ['انگیزه', 'انگیزشی', 'تشویق', 'انگیزه', 'انگیزه‌دهنده']
            }
            
            for category_id, keywords in category_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    categories = await qa_service.get_categories()
                    return next((c for c in categories if c['category_id'] == category_id), None)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Analyze question category failed: {e}")
            return None


# Global Q&A handler instance
qa_handler = QAHandler()
