"""
🌌 SarlakBot v3.0 - Menu Admin Commands
Admin commands for menu management and route synchronization
"""

import json
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.config import config
from src.core.route_registry import route_registry
from src.core.menu_manager import menu_manager
from src.core.preflight_validator import PreflightValidator
from src.utils.logging import get_logger

logger = get_logger(__name__)


class MenuAdminHandler:
    """
    🌌 Menu Admin Handler
    Handles admin commands for menu management
    """
    
    def __init__(self):
        self.logger = logger
    
    async def handle_sync_menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /sync_menu command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Check admin permission
            if user_id != config.bot.admin_id:
                await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
                return
            
            self.logger.info(f"Admin {user_id} requested menu sync")
            
            # Show sync status
            status_message = await update.message.reply_text("🔄 در حال همگام‌سازی منوها...")
            
            # Sync routes
            success = await route_registry.sync_to_database()
            
            if success:
                # Update menu cache
                await menu_manager.update_menu_cache()
                
                # Get validation results
                validation_results = await route_registry.validate_routes()
                
                # Prepare response
                response_text = "✅ **همگام‌سازی منوها تکمیل شد!**\n\n"
                
                if validation_results['info']:
                    response_text += "📊 **آمار:**\n"
                    for info in validation_results['info']:
                        response_text += f"• {info}\n"
                
                if validation_results['warnings']:
                    response_text += "\n⚠️ **هشدارها:**\n"
                    for warning in validation_results['warnings']:
                        response_text += f"• {warning}\n"
                
                if validation_results['errors']:
                    response_text += "\n❌ **خطاها:**\n"
                    for error in validation_results['errors']:
                        response_text += f"• {error}\n"
                
                await status_message.edit_text(response_text, parse_mode='Markdown')
                
            else:
                await status_message.edit_text("❌ **همگام‌سازی منوها ناموفق بود!**\n\nلطفاً لاگ‌ها را بررسی کنید.")
            
        except Exception as e:
            self.logger.error(f"Sync menu command failed: {e}")
            await update.message.reply_text("❌ خطا در همگام‌سازی منوها.")
    
    async def handle_validate_routes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /validate_routes command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Check admin permission
            if user_id != config.bot.admin_id:
                await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
                return
            
            self.logger.info(f"Admin {user_id} requested route validation")
            
            # Show validation status
            status_message = await update.message.reply_text("🔍 در حال اعتبارسنجی route ها...")
            
            # Validate routes
            validation_results = await route_registry.validate_routes()
            
            # Prepare response
            response_text = "🔍 **نتایج اعتبارسنجی Route ها:**\n\n"
            
            if validation_results['info']:
                response_text += "📊 **اطلاعات:**\n"
                for info in validation_results['info']:
                    response_text += f"• {info}\n"
            
            if validation_results['warnings']:
                response_text += "\n⚠️ **هشدارها:**\n"
                for warning in validation_results['warnings']:
                    response_text += f"• {warning}\n"
            
            if validation_results['errors']:
                response_text += "\n❌ **خطاها:**\n"
                for error in validation_results['errors']:
                    response_text += f"• {error}\n"
            
            if not validation_results['errors'] and not validation_results['warnings']:
                response_text += "✅ **همه چیز درست است!**"
            
            await status_message.edit_text(response_text, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Validate routes command failed: {e}")
            await update.message.reply_text("❌ خطا در اعتبارسنجی route ها.")
    
    async def handle_export_routes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /export_routes command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Check admin permission
            if user_id != config.bot.admin_id:
                await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
                return
            
            self.logger.info(f"Admin {user_id} requested route export")
            
            # Show export status
            status_message = await update.message.reply_text("📤 در حال export کردن route ها...")
            
            # Export routes
            export_data = await route_registry.export_routes()
            
            if export_data:
                # Save to file
                filename = f"routes_export_{user_id}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                # Send file
                with open(filename, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=filename,
                        caption="📤 **Export Route ها تکمیل شد!**\n\nفایل JSON حاوی تمام route ها و منوها."
                    )
                
                await status_message.delete()
                
            else:
                await status_message.edit_text("❌ **Export ناموفق بود!**")
            
        except Exception as e:
            self.logger.error(f"Export routes command failed: {e}")
            await update.message.reply_text("❌ خطا در export کردن route ها.")
    
    async def handle_preflight_check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /preflight_check command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Check admin permission
            if user_id != config.bot.admin_id:
                await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
                return
            
            self.logger.info(f"Admin {user_id} requested preflight check")
            
            # Show check status
            status_message = await update.message.reply_text("🚀 در حال اجرای preflight checks...")
            
            # Run preflight checks
            validator = PreflightValidator()
            success = await validator.run_all_checks()
            
            # Prepare response
            response_text = "🚀 **نتایج Preflight Checks:**\n\n"
            response_text += f"✅ **Checks Passed:** {validator.checks_passed}\n"
            response_text += f"❌ **Checks Failed:** {validator.checks_failed}\n\n"
            
            if validator.failed_checks:
                response_text += "❌ **خطاها:**\n"
                for check in validator.failed_checks:
                    response_text += f"• {check}\n"
            
            if validator.warnings:
                response_text += "\n⚠️ **هشدارها:**\n"
                for warning in validator.warnings:
                    response_text += f"• {warning}\n"
            
            if validator.info:
                response_text += "\nℹ️ **اطلاعات:**\n"
                for info in validator.info:
                    response_text += f"• {info}\n"
            
            if success:
                response_text += "\n🎉 **همه چیز آماده است!**"
            else:
                response_text += "\n🚫 **Deployment مسدود است!**"
            
            await status_message.edit_text(response_text, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Preflight check command failed: {e}")
            await update.message.reply_text("❌ خطا در اجرای preflight checks.")
    
    async def handle_menu_tree_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /menu_tree command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Check admin permission
            if user_id != config.bot.admin_id:
                await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
                return
            
            self.logger.info(f"Admin {user_id} requested menu tree")
            
            # Get menu tree
            menu_tree = await menu_manager.get_menu_tree()
            
            if menu_tree:
                # Convert to readable format
                tree_text = self._format_menu_tree(menu_tree)
                
                # Send as file if too long
                if len(tree_text) > 4000:
                    filename = f"menu_tree_{user_id}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(tree_text)
                    
                    with open(filename, 'rb') as f:
                        await update.message.reply_document(
                            document=f,
                            filename=filename,
                            caption="🌳 **درخت منوها**"
                        )
                else:
                    await update.message.reply_text(f"🌳 **درخت منوها:**\n\n```\n{tree_text}\n```", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ **درخت منوها یافت نشد!**")
            
        except Exception as e:
            self.logger.error(f"Menu tree command failed: {e}")
            await update.message.reply_text("❌ خطا در دریافت درخت منوها.")
    
    def _format_menu_tree(self, tree: Dict[str, Any], level: int = 0) -> str:
        """Format menu tree for display"""
        indent = "  " * level
        result = ""
        
        if 'button_text' in tree:
            result += f"{indent}📁 {tree['button_text']} ({tree.get('route_key', 'unknown')})\n"
        else:
            result += f"{indent}🌳 {tree.get('route_key', 'root')}\n"
        
        for child in tree.get('children', []):
            result += self._format_menu_tree(child, level + 1)
        
        return result
    
    async def handle_clear_cache_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear_cache command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Check admin permission
            if user_id != config.bot.admin_id:
                await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
                return
            
            self.logger.info(f"Admin {user_id} requested cache clear")
            
            # Clear menu cache
            await menu_manager.clear_cache()
            
            await update.message.reply_text("✅ **Cache منوها پاک شد!**")
            
        except Exception as e:
            self.logger.error(f"Clear cache command failed: {e}")
            await update.message.reply_text("❌ خطا در پاک کردن cache.")
    
    async def register_admin_commands(self, application) -> None:
        """Register admin commands"""
        try:
            from telegram.ext import CommandHandler
            
            # Register admin commands
            application.add_handler(CommandHandler("sync_menu", self.handle_sync_menu_command))
            application.add_handler(CommandHandler("validate_routes", self.handle_validate_routes_command))
            application.add_handler(CommandHandler("export_routes", self.handle_export_routes_command))
            application.add_handler(CommandHandler("preflight_check", self.handle_preflight_check_command))
            application.add_handler(CommandHandler("menu_tree", self.handle_menu_tree_command))
            application.add_handler(CommandHandler("clear_cache", self.handle_clear_cache_command))
            
            self.logger.info("✅ Menu admin commands registered")
            
        except Exception as e:
            self.logger.error(f"Failed to register admin commands: {e}")
            raise


# Global menu admin handler instance
menu_admin_handler = MenuAdminHandler()



