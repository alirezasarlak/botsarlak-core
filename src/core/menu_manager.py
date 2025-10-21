"""
🌌 SarlakBot v3.0 - Menu Manager
Dynamic menu generation and management system
"""

import json
from typing import Dict, List, Any, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.core.route_registry import route_registry, RouteType
from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class MenuManager:
    """
    🌌 Menu Manager
    Dynamic menu generation and management
    """
    
    def __init__(self):
        self.logger = logger
        self._menu_cache: Dict[str, InlineKeyboardMarkup] = {}
    
    async def get_menu(self, route_key: str, user_id: Optional[int] = None) -> Optional[InlineKeyboardMarkup]:
        """
        Get menu for a specific route
        
        Args:
            route_key: Route key for the menu
            user_id: User ID for personalized menus
            
        Returns:
            InlineKeyboardMarkup or None
        """
        try:
            # Check cache first
            cache_key = f"{route_key}_{user_id or 'default'}"
            if cache_key in self._menu_cache:
                return self._menu_cache[cache_key]
            
            # Get routes for this parent
            routes = await self._get_routes_by_parent(route_key)
            
            if not routes:
                self.logger.warning(f"No routes found for parent: {route_key}")
                return None
            
            # Generate keyboard
            keyboard = await self._generate_keyboard(routes, user_id)
            
            if keyboard:
                # Cache the result
                self._menu_cache[cache_key] = keyboard
            
            return keyboard
            
        except Exception as e:
            self.logger.error(f"Failed to get menu for {route_key}: {e}")
            return None
    
    async def _get_routes_by_parent(self, parent_key: str) -> List[Dict[str, Any]]:
        """Get routes by parent key"""
        try:
            query = """
                SELECT * FROM routes 
                WHERE parent_route = $1 AND is_active = TRUE 
                ORDER BY order_num, route_key
            """
            
            routes = await db_manager.fetch_all(query, parent_key)
            return routes
            
        except Exception as e:
            self.logger.error(f"Failed to get routes by parent {parent_key}: {e}")
            return []
    
    async def _generate_keyboard(self, routes: List[Dict[str, Any]], user_id: Optional[int] = None) -> Optional[InlineKeyboardMarkup]:
        """Generate keyboard from routes"""
        try:
            if not routes:
                return None
            
            # Group routes into rows (max 2 buttons per row)
            keyboard = []
            current_row = []
            
            for route in routes:
                button_text = route['button_text']
                route_key = route['route_key']
                route_type = route['route_type']
                
                # Create callback data based on route type
                if route_type == 'menu':
                    callback_data = f"menu_{route_key}"
                elif route_type == 'action':
                    callback_data = f"action_{route_key}"
                else:
                    callback_data = f"route_{route_key}"
                
                # Create button
                button = InlineKeyboardButton(button_text, callback_data=callback_data)
                current_row.append(button)
                
                # Add row if it has 2 buttons or if it's the last route
                if len(current_row) == 2 or route == routes[-1]:
                    keyboard.append(current_row)
                    current_row = []
            
            # Add navigation buttons
            navigation_buttons = await self._get_navigation_buttons(route_key)
            if navigation_buttons:
                keyboard.append(navigation_buttons)
            
            return InlineKeyboardMarkup(keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to generate keyboard: {e}")
            return None
    
    async def _get_navigation_buttons(self, current_route: str) -> List[InlineKeyboardButton]:
        """Get navigation buttons for current route"""
        try:
            buttons = []
            
            # Get parent route
            parent_query = """
                SELECT parent_route FROM routes 
                WHERE route_key = $1
            """
            
            parent_result = await db_manager.fetch_one(parent_query, current_route)
            
            if parent_result and parent_result['parent_route']:
                # Add back button
                buttons.append(InlineKeyboardButton("🔙 بازگشت", callback_data=f"menu_{parent_result['parent_route']}"))
            
            # Add home button
            buttons.append(InlineKeyboardButton("🏠 خانه", callback_data="menu_main"))
            
            return buttons
            
        except Exception as e:
            self.logger.error(f"Failed to get navigation buttons: {e}")
            return []
    
    async def get_breadcrumb(self, route_key: str) -> str:
        """Get breadcrumb path for a route"""
        try:
            breadcrumb_parts = []
            current_route = route_key
            
            while current_route:
                # Get route info
                query = """
                    SELECT route_key, button_text, parent_route 
                    FROM routes 
                    WHERE route_key = $1
                """
                
                route_info = await db_manager.fetch_one(query, current_route)
                
                if route_info:
                    breadcrumb_parts.insert(0, route_info['button_text'])
                    current_route = route_info['parent_route']
                else:
                    break
            
            return " > ".join(breadcrumb_parts) if breadcrumb_parts else "منوی اصلی"
            
        except Exception as e:
            self.logger.error(f"Failed to get breadcrumb for {route_key}: {e}")
            return "منوی اصلی"
    
    async def clear_cache(self, route_key: Optional[str] = None):
        """Clear menu cache"""
        try:
            if route_key:
                # Clear specific route cache
                keys_to_remove = [key for key in self._menu_cache.keys() if key.startswith(route_key)]
                for key in keys_to_remove:
                    del self._menu_cache[key]
            else:
                # Clear all cache
                self._menu_cache.clear()
            
            self.logger.info(f"Menu cache cleared for: {route_key or 'all'}")
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
    
    async def get_menu_tree(self) -> Dict[str, Any]:
        """Get complete menu tree"""
        try:
            # Get menu tree from database
            query = """
                SELECT menu_json FROM menus 
                WHERE menu_name = 'main_menu' 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            
            result = await db_manager.fetch_one(query)
            
            if result:
                return json.loads(result['menu_json'])
            else:
                # Generate menu tree if not exists
                return await self._generate_menu_tree()
                
        except Exception as e:
            self.logger.error(f"Failed to get menu tree: {e}")
            return {}
    
    async def _generate_menu_tree(self) -> Dict[str, Any]:
        """Generate menu tree from routes"""
        try:
            # Get all routes
            query = """
                SELECT * FROM routes 
                WHERE is_active = TRUE 
                ORDER BY parent_route, order_num, route_key
            """
            
            routes = await db_manager.fetch_all(query)
            
            # Build tree structure
            tree = {'route_key': 'root', 'children': []}
            
            # Group routes by parent
            by_parent = {}
            for route in routes:
                parent = route['parent_route'] or 'root'
                if parent not in by_parent:
                    by_parent[parent] = []
                by_parent[parent].append(route)
            
            # Build tree recursively
            def build_node(parent_key: str) -> Dict[str, Any]:
                node = {
                    'route_key': parent_key,
                    'children': []
                }
                
                if parent_key in by_parent:
                    children = sorted(by_parent[parent_key], key=lambda x: (x['order_num'], x['route_key']))
                    
                    for child in children:
                        child_node = {
                            'route_key': child['route_key'],
                            'button_text': child['button_text'],
                            'route_type': child['route_type'],
                            'metadata': json.loads(child['metadata']) if child['metadata'] else {},
                            'children': []
                        }
                        
                        # Recursively build children
                        child_children = build_node(child['route_key'])
                        child_node['children'] = child_children['children']
                        
                        node['children'].append(child_node)
                
                return node
            
            return build_node('root')
            
        except Exception as e:
            self.logger.error(f"Failed to generate menu tree: {e}")
            return {}
    
    async def update_menu_cache(self):
        """Update menu cache after route changes"""
        try:
            # Clear all cache
            await self.clear_cache()
            
            # Pre-generate common menus
            common_menus = ['main', 'study', 'profile', 'settings']
            
            for menu_key in common_menus:
                await self.get_menu(menu_key)
            
            self.logger.info("Menu cache updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update menu cache: {e}")


# Global menu manager instance
menu_manager = MenuManager()



