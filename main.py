#!/usr/bin/env python3
"""
🌌 SarlakBot - Clean Rebuild
VERSION: v2.4.0-profile-gamification
LAST_UPDATE: 2025-10-18
Professional Educational Companion for Iranian University Entrance Exam

Architecture: Clean Architecture with SOLID principles
Features: Viral growth, scalable, Gen-Z friendly, cosmic journey
Author: Sarlak Academy Team
Python: 3.10+
"""

import asyncio
import signal
import sys

# Version constants
__version__ = "v3.2.0-ai-coach-system"
__last_update__ = "2025-01-21"

from telegram import Update
from telegram.ext import AIORateLimiter, Application

from src.config import config
from src.database.connection import db_manager
from src.handlers.admin.handler import AdminHandler
from src.handlers.admin.ops_handler import ops_handler
from src.handlers.ai_coach.ai_coach_integration import ai_coach_integration
from src.handlers.league.league_handler import LeagueHandler
from src.handlers.main_menu.handler import MainMenuHandler
from src.handlers.qa.qa_handler import qa_handler
from src.handlers.referral.handler import ReferralHandler
from src.handlers.report.report_handler import ReportHandler
from src.handlers.start_handler import start_handler
from src.handlers.profile_creation_handler import profile_creation_handler
from src.utils.logging import get_logger, setup_logging

# from src.monitoring.system_monitor import system_monitor


class SarlakBot:
    """
    🌌 SarlakBot v3.0 - Gen-Z Cosmic Study Journey

    Features:
    - Clean Architecture with SOLID principles
    - Gen-Z friendly cosmic journey experience
    - Viral growth mechanisms
    - Scalable and modular design
    - Professional error handling
    - Real-time monitoring
    """

    def __init__(self):
        self.config = config
        self.application: Application | None = None
        self.logger = get_logger(__name__)

        # Initialize handlers
        self.start_handler = start_handler
        self.profile_creation_handler = profile_creation_handler
        self.main_menu_handler = MainMenuHandler()
        self.admin_handler = AdminHandler()
        self.ops_handler = ops_handler
        self.qa_handler = qa_handler
        self.referral_handler = ReferralHandler()
        self.report_handler = ReportHandler()
        self.league_handler = LeagueHandler()
        self.ai_coach_integration = ai_coach_integration

    async def initialize(self) -> None:
        """Initialize all bot components"""
        try:
            self.logger.info("🌌 Initializing SarlakBot v3.0 - Gen-Z Cosmic Study Journey...")

            # Setup logging
            setup_logging(
                log_level=self.config.monitoring.log_level, enable_json=self.config.is_production
            )

            # Initialize database
            await db_manager.initialize()

            # Setup AI Coach system
            await self.ai_coach_integration.setup_ai_coach_system()

            # Create Telegram application with persistence
            from telegram.ext import PicklePersistence
            persistence = PicklePersistence(filepath="bot_data.pkl")
            
            self.application = (
                Application.builder()
                .token(self.config.bot.token)
                .rate_limiter(AIORateLimiter())
                .persistence(persistence)
                .build()
            )

            # Register handlers
            await self._register_handlers()

            # Start health server in background (disabled for now)
            # asyncio.create_task(start_health_server())

            # Start system monitoring (disabled for now - requires psutil)
            # asyncio.create_task(system_monitor.start_monitoring(interval=300))  # 5 minutes
            # self.logger.info("🔍 System monitoring started")

            self.logger.info("✅ SarlakBot v3.0 initialization completed successfully!")
            self.logger.info("🚀 Ready to embark on cosmic study journeys with Gen-Z students!")
            self.logger.info("🏥 Health server disabled for now")

        except Exception as e:
            self.logger.error(f"❌ SarlakBot initialization failed: {e}")
            raise

    async def _register_handlers(self) -> None:
        """Register all bot handlers"""
        try:
            self.logger.info("📝 Registering bot handlers...")

            # Register start handler
            await self.start_handler.register(self.application)
            self.logger.info("✅ Start handler registered")

            # Register profile creation handler
            await self.profile_creation_handler.register(self.application)
            self.logger.info("✅ Profile creation handler registered")

            # Register main menu handler
            if self.config.features.profile_v1:
                await self.main_menu_handler.register(self.application)
                self.logger.info("✅ Main menu handler registered")

            # Register Q&A handler
            await self.qa_handler.register(self.application)
            self.logger.info("✅ Q&A Handler registered")

            # Register report handler
            if self.config.features.report_v1:
                await self.report_handler.register(self.application)
                self.logger.info("✅ Report Handler registered")

            # Register league handler
            if self.config.features.league_v1:
                await self.league_handler.register(self.application)
                self.logger.info("✅ League Handler registered")

            # Register auto tracking (integrated in report handler)
            if self.config.features.auto_tracking_v1:
                self.logger.info("✅ Auto Tracking Service enabled")

            # Register admin handler
            await self.admin_handler.register(self.application)
            self.logger.info("✅ Admin handler registered")

            # Register operations handler
            await self.ops_handler.register(self.application)
            self.logger.info("✅ Operations handler registered")

            # Register AI Coach handlers
            ai_coach_handlers = self.ai_coach_integration.get_handlers()
            for handler in ai_coach_handlers:
                self.application.add_handler(handler)
            self.logger.info("✅ AI Coach handlers registered")

            # TODO: Register other handlers as they are implemented
            # - Motivation handler
            # - Competition handler
            # - Store handler

            self.logger.info("🎯 All handlers registered successfully")

        except Exception as e:
            self.logger.error(f"❌ Handler registration failed: {e}")
            raise

    async def start(self) -> None:
        """Start the bot"""
        try:
            if not self.application:
                raise RuntimeError("Bot not initialized")

            self.logger.info("🚀 Starting SarlakBot v3.0...")
            self.logger.info("🌌 Welcome to the cosmic study journey!")

            # Start the bot
            await self.application.initialize()
            await self.application.start()

            self.logger.info("✨ SarlakBot v3.0 is now running and ready to serve students!")
            self.logger.info("🎯 Students can now start their cosmic study journey!")

            # Keep the bot running
            self.logger.info("🚀 Starting polling...")
            
            # Start polling in background task
            polling_task = asyncio.create_task(
                self.application.updater.start_polling(
                    drop_pending_updates=True, 
                    allowed_updates=Update.ALL_TYPES
                )
            )
            
            # Keep running indefinitely
            self.logger.info("✅ Bot is now running and polling for updates")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("🛑 Received interrupt signal")
                polling_task.cancel()

        except Exception as e:
            self.logger.error(f"❌ SarlakBot startup failed: {e}")
            raise

    async def stop(self) -> None:
        """Stop the bot gracefully"""
        try:
            self.logger.info("🛑 Stopping SarlakBot v3.0...")

            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()

            await db_manager.close()

            self.logger.info("✅ SarlakBot v3.0 stopped gracefully")
            self.logger.info("👋 See you in the next cosmic journey!")

        except Exception as e:
            self.logger.error(f"❌ Error during SarlakBot shutdown: {e}")


async def main():
    """Main entry point"""
    bot = SarlakBot()

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(bot.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await bot.initialize()
        await bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Keyboard interrupt received")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye! See you in the next cosmic journey!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
