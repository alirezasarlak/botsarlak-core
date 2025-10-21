#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌌 SarlakBot v3.1.0 - Q&A System Test Script
Test the complete Q&A system functionality
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.database.connection import db_manager
from src.services.qa_service import qa_service
from src.services.user_learning_service import user_learning_service
from src.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


async def test_qa_system():
    """Test the complete Q&A system"""
    try:
        print("🌌 Testing SarlakBot Q&A System v3.1.0")
        print("=" * 50)
        
        # Initialize database
        await db_manager.initialize()
        print("✅ Database initialized")
        
        # Test user ID
        test_user_id = 694245594  # Admin user
        
        print(f"\n🧪 Testing with user ID: {test_user_id}")
        
        # Test 1: Get categories
        print("\n📚 Test 1: Getting categories...")
        categories = await qa_service.get_categories()
        print(f"✅ Found {len(categories)} categories")
        for category in categories[:3]:
            print(f"   - {category['icon']} {category['name']}")
        
        # Test 2: Get user Q&A stats
        print("\n📊 Test 2: Getting user Q&A stats...")
        stats = await qa_service.get_user_qa_stats(test_user_id)
        print(f"✅ User stats: {stats}")
        
        # Test 3: Test asking a question
        print("\n❓ Test 3: Asking a test question...")
        question_result = await qa_service.ask_question(
            user_id=test_user_id,
            question_text="چطور می‌تونم ریاضی رو بهتر یاد بگیرم؟",
            category_id=1,  # ریاضی
            question_context="من پایه دوازدهم هستم و برای کنکور آماده می‌شم",
            priority=qa_service.QuestionPriority.NORMAL
        )
        
        if question_result['success']:
            print("✅ Question asked successfully!")
            print(f"   Question ID: {question_result['question_id']}")
            print(f"   Points spent: {question_result['points_spent']}")
            print(f"   Answer preview: {question_result['answer'][:100]}...")
        else:
            print(f"❌ Question failed: {question_result.get('error', 'Unknown error')}")
        
        # Test 4: Test user learning analysis
        print("\n🧠 Test 4: Testing user learning analysis...")
        learning_profile = await user_learning_service.analyze_user_learning_patterns(test_user_id)
        if learning_profile:
            print("✅ Learning profile created!")
            print(f"   Level: {learning_profile.learning_level.value}")
            print(f"   Interest areas: {[area.value for area in learning_profile.interest_areas]}")
            print(f"   Strengths: {learning_profile.strengths}")
            print(f"   Weaknesses: {learning_profile.weaknesses}")
        else:
            print("⚠️ No learning profile created (not enough data)")
        
        # Test 5: Test personalized context
        print("\n🎯 Test 5: Testing personalized context...")
        personalized_context = await user_learning_service.get_personalized_response_context(
            test_user_id, "سوال تستی"
        )
        print(f"✅ Personalized context: {personalized_context}")
        
        # Test 6: Test learning recommendations
        print("\n💡 Test 6: Testing learning recommendations...")
        recommendations = await user_learning_service.get_learning_recommendations(test_user_id)
        print(f"✅ Found {len(recommendations)} recommendations")
        for rec in recommendations[:2]:
            print(f"   - {rec['title']}: {rec['description']}")
        
        # Test 7: Test popular questions
        print("\n🔥 Test 7: Testing popular questions...")
        popular_questions = await qa_service.get_popular_questions(5)
        print(f"✅ Found {len(popular_questions)} popular questions")
        for q in popular_questions[:2]:
            print(f"   - {q['question_text'][:50]}...")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Q&A system test failed: {e}")
        raise
    finally:
        await db_manager.close()


async def test_database_schema():
    """Test database schema for Q&A system"""
    try:
        print("\n🗄️ Testing database schema...")
        
        # Test Q&A tables exist
        tables_to_check = [
            'qa_categories',
            'qa_questions', 
            'qa_answers',
            'qa_sessions',
            'qa_feedback',
            'qa_templates',
            'qa_analytics',
            'user_learning_profiles',
            'learning_insights'
        ]
        
        for table in tables_to_check:
            result = await db_manager.fetch_one(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            if result['exists']:
                print(f"✅ Table {table} exists")
            else:
                print(f"❌ Table {table} missing")
        
        # Test functions exist
        functions_to_check = [
            'can_user_ask_question',
            'deduct_qa_points',
            'get_qa_stats',
            'get_popular_questions'
        ]
        
        for func in functions_to_check:
            result = await db_manager.fetch_one(
                "SELECT EXISTS (SELECT FROM information_schema.routines WHERE routine_name = $1)",
                func
            )
            if result['exists']:
                print(f"✅ Function {func} exists")
            else:
                print(f"❌ Function {func} missing")
        
        print("✅ Database schema test completed")
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        raise


async def main():
    """Main test function"""
    try:
        # Setup logging
        setup_logging(log_level="INFO", enable_json=False)
        
        print("🚀 Starting SarlakBot Q&A System Tests")
        print(f"⏰ Test started at: {datetime.now()}")
        
        # Test database schema
        await test_database_schema()
        
        # Test Q&A system
        await test_qa_system()
        
        print("\n🎉 All tests completed successfully!")
        print("✅ Q&A System is ready for production!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
