"""
🌌 SarlakBot v3.0 - Route Registry System
The Living Map - Self-healing, auto-synchronized route management
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import inspect

from src.utils.logging import get_logger
from src.database.connection import db_manager

logger = get_logger(__name__)


class RouteType(Enum):
    """Route types for different functionalities"""
    MENU = "menu"
    ACTION = "action"
    CALLBACK = "callback"
    COMMAND = "command"
    CONVERSATION = "conversation"


@dataclass
class RouteInfo:
    """Route information container"""
    route_key: str
    handler_name: str
    button_text: str
    parent_route: Optional[str] = None
    order_num: int = 0
    route_type: RouteType = RouteType.MENU
    is_active: bool = True
    handler_function: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class RouteRegistry:
    """
    🌌 Route Registry - The Living Map
    Master singleton for all routes, menus, and handlers
    """
    
    _instance: Optional['RouteRegistry'] = None
    _routes: Dict[str, RouteInfo] = {}
    _menu_tree: Dict[str, Any] = {}
    _initialized: bool = False
    
    def __new__(cls) -> 'RouteRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = logger
            self._initialized = True
    
    @classmethod
    def register(
        cls,
        route_key: str,
        button_text: str,
        parent: Optional[str] = None,
        order: int = 0,
        route_type: RouteType = RouteType.MENU,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Callable:
        """
        Decorator to register routes
        
        Args:
            route_key: Unique route identifier (e.g., "study.report")
            button_text: Display text for button/menu
            parent: Parent route key (None for root)
            order: Display order
            route_type: Type of route
            metadata: Additional metadata
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            # Get the handler name from the function
            handler_name = f"{func.__module__}.{func.__name__}"
            
            # Create route info
            route_info = RouteInfo(
                route_key=route_key,
                handler_name=handler_name,
                button_text=button_text,
                parent_route=parent,
                order_num=order,
                route_type=route_type,
                handler_function=func,
                metadata=metadata or {}
            )
            
            # Register the route
            cls._instance._routes[route_key] = route_info
            
            self.logger.info(f"✅ Registered route: {route_key} -> {handler_name}")
            
            return func
        
        return decorator
    
    async def sync_to_database(self) -> bool:
        """
        Synchronize routes to database
        
        Returns:
            Success status
        """
        try:
            self.logger.info("🔄 Synchronizing routes to database...")
            
            # Get existing routes from database
            existing_routes = await self._get_existing_routes()
            
            # Process each registered route
            for route_key, route_info in self._routes.items():
                await self._upsert_route(route_info, existing_routes)
            
            # Mark orphan routes as inactive
            await self._mark_orphan_routes_inactive(existing_routes)
            
            # Rebuild menu tree
            await self._rebuild_menu_tree()
            
            # Log sync completion
            await self._log_route_action("sync", "all", {"routes_count": len(self._routes)})
            
            self.logger.info("✅ Route synchronization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Route synchronization failed: {e}")
            return False
    
    async def _get_existing_routes(self) -> Dict[str, Dict[str, Any]]:
        """Get existing routes from database"""
        try:
            query = "SELECT * FROM routes"
            rows = await db_manager.fetch_all(query)
            
            return {row['route_key']: row for row in rows}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get existing routes: {e}")
            return {}
    
    async def _upsert_route(self, route_info: RouteInfo, existing_routes: Dict[str, Any]) -> None:
        """Upsert route to database"""
        try:
            existing = existing_routes.get(route_info.route_key)
            
            if existing:
                # Update existing route
                query = """
                    UPDATE routes SET
                        handler_name = $2,
                        button_text = $3,
                        parent_route = $4,
                        order_num = $5,
                        route_type = $6,
                        is_active = $7,
                        metadata = $8,
                        updated_at = NOW()
                    WHERE route_key = $1
                """
                
                await db_manager.execute(
                    query,
                    route_info.route_key,
                    route_info.handler_name,
                    route_info.button_text,
                    route_info.parent_route,
                    route_info.order_num,
                    route_info.route_type.value,
                    route_info.is_active,
                    json.dumps(route_info.metadata)
                )
                
                self.logger.debug(f"🔄 Updated route: {route_info.route_key}")
                
            else:
                # Insert new route
                query = """
                    INSERT INTO routes (
                        route_key, handler_name, button_text, parent_route,
                        order_num, route_type, is_active, metadata, created_at, updated_at
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW()
                    )
                """
                
                await db_manager.execute(
                    query,
                    route_info.route_key,
                    route_info.handler_name,
                    route_info.button_text,
                    route_info.parent_route,
                    route_info.order_num,
                    route_info.route_type.value,
                    route_info.is_active,
                    json.dumps(route_info.metadata)
                )
                
                self.logger.debug(f"➕ Added route: {route_info.route_key}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to upsert route {route_info.route_key}: {e}")
    
    async def _mark_orphan_routes_inactive(self, existing_routes: Dict[str, Any]) -> None:
        """Mark routes that are no longer in code as inactive"""
        try:
            registered_keys = set(self._routes.keys())
            existing_keys = set(existing_routes.keys())
            
            orphan_keys = existing_keys - registered_keys
            
            for route_key in orphan_keys:
                query = """
                    UPDATE routes SET
                        is_active = FALSE,
                        updated_at = NOW()
                    WHERE route_key = $1
                """
                
                await db_manager.execute(query, route_key)
                self.logger.warning(f"⚠️ Marked orphan route as inactive: {route_key}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to mark orphan routes: {e}")
    
    async def _rebuild_menu_tree(self) -> None:
        """Rebuild the menu tree from routes"""
        try:
            # Get all active routes
            query = """
                SELECT * FROM routes 
                WHERE is_active = TRUE 
                ORDER BY parent_route, order_num, route_key
            """
            
            routes = await db_manager.fetch_all(query)
            
            # Build tree structure
            tree = self._build_tree_structure(routes)
            
            # Store menu tree
            menu_json = json.dumps(tree, ensure_ascii=False, indent=2)
            
            # Upsert menu
            query = """
                INSERT INTO menus (menu_name, menu_json, version, created_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (menu_name) 
                DO UPDATE SET
                    menu_json = EXCLUDED.menu_json,
                    version = EXCLUDED.version,
                    updated_at = NOW()
            """
            
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            await db_manager.execute(query, "main_menu", menu_json, version)
            
            self._menu_tree = tree
            self.logger.info("✅ Menu tree rebuilt successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rebuild menu tree: {e}")
    
    def _build_tree_structure(self, routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build hierarchical tree structure from routes"""
        tree = {}
        
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
    
    async def _log_route_action(self, action: str, route_key: str, payload: Dict[str, Any]) -> None:
        """Log route actions for audit trail"""
        try:
            query = """
                INSERT INTO route_history (action, route_key, payload, created_at)
                VALUES ($1, $2, $3, NOW())
            """
            
            await db_manager.execute(query, action, route_key, json.dumps(payload))
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log route action: {e}")
    
    async def validate_routes(self) -> Dict[str, List[str]]:
        """
        Validate all routes for integrity
        
        Returns:
            Dictionary of validation results
        """
        results = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        try:
            # Check for duplicate route keys
            route_keys = [route.route_key for route in self._routes.values()]
            duplicates = [key for key in set(route_keys) if route_keys.count(key) > 1]
            
            if duplicates:
                results['errors'].append(f"Duplicate route keys: {duplicates}")
            
            # Check for missing handlers
            for route_key, route_info in self._routes.items():
                if not route_info.handler_function:
                    results['errors'].append(f"Missing handler for route: {route_key}")
            
            # Check for circular references
            circular = self._check_circular_references()
            if circular:
                results['errors'].append(f"Circular references found: {circular}")
            
            # Check menu depth
            max_depth = self._get_max_menu_depth()
            if max_depth > 3:
                results['warnings'].append(f"Menu depth exceeds 3 levels: {max_depth}")
            
            # Check button count per page
            button_counts = self._get_button_counts_per_page()
            for parent, count in button_counts.items():
                if count > 8:
                    results['warnings'].append(f"Too many buttons in {parent}: {count} (max 8)")
            
            results['info'].append(f"Total routes: {len(self._routes)}")
            results['info'].append(f"Active routes: {sum(1 for r in self._routes.values() if r.is_active)}")
            
        except Exception as e:
            results['errors'].append(f"Validation failed: {e}")
        
        return results
    
    def _check_circular_references(self) -> List[str]:
        """Check for circular references in route hierarchy"""
        circular = []
        
        def check_route(route_key: str, visited: set) -> bool:
            if route_key in visited:
                return True
            
            visited.add(route_key)
            
            for route in self._routes.values():
                if route.parent_route == route_key:
                    if check_route(route.route_key, visited.copy()):
                        circular.append(route_key)
                        return True
            
            return False
        
        for route_key in self._routes.keys():
            check_route(route_key, set())
        
        return circular
    
    def _get_max_menu_depth(self) -> int:
        """Get maximum menu depth"""
        def get_depth(route_key: str, visited: set = None) -> int:
            if visited is None:
                visited = set()
            
            if route_key in visited:
                return 0
            
            visited.add(route_key)
            
            max_child_depth = 0
            for route in self._routes.values():
                if route.parent_route == route_key:
                    child_depth = get_depth(route.route_key, visited.copy())
                    max_child_depth = max(max_child_depth, child_depth)
            
            return 1 + max_child_depth
        
        max_depth = 0
        for route_key in self._routes.keys():
            depth = get_depth(route_key)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _get_button_counts_per_page(self) -> Dict[str, int]:
        """Get button counts per parent page"""
        counts = {}
        
        for route in self._routes.values():
            parent = route.parent_route or 'root'
            counts[parent] = counts.get(parent, 0) + 1
        
        return counts
    
    async def export_routes(self) -> Dict[str, Any]:
        """Export routes to JSON format"""
        try:
            export_data = {
                'version': datetime.now().strftime("%Y%m%d_%H%M%S"),
                'routes': [],
                'menu_tree': self._menu_tree
            }
            
            for route in self._routes.values():
                route_data = {
                    'route_key': route.route_key,
                    'handler_name': route.handler_name,
                    'button_text': route.button_text,
                    'parent_route': route.parent_route,
                    'order_num': route.order_num,
                    'route_type': route.route_type.value,
                    'is_active': route.is_active,
                    'metadata': route.metadata
                }
                export_data['routes'].append(route_data)
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export routes: {e}")
            return {}
    
    async def import_routes(self, import_data: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """
        Import routes from JSON format
        
        Args:
            import_data: Routes data to import
            dry_run: If True, only validate without importing
            
        Returns:
            Import results
        """
        results = {
            'success': True,
            'imported': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            if 'routes' not in import_data:
                results['errors'].append("Invalid import data: missing 'routes' key")
                results['success'] = False
                return results
            
            # Validate import data
            for route_data in import_data['routes']:
                required_fields = ['route_key', 'handler_name', 'button_text']
                for field in required_fields:
                    if field not in route_data:
                        results['errors'].append(f"Missing required field '{field}' in route")
                        results['success'] = False
            
            if not results['success']:
                return results
            
            if not dry_run:
                # Import routes
                for route_data in import_data['routes']:
                    route_info = RouteInfo(
                        route_key=route_data['route_key'],
                        handler_name=route_data['handler_name'],
                        button_text=route_data['button_text'],
                        parent_route=route_data.get('parent_route'),
                        order_num=route_data.get('order_num', 0),
                        route_type=RouteType(route_data.get('route_type', 'menu')),
                        is_active=route_data.get('is_active', True),
                        metadata=route_data.get('metadata', {})
                    )
                    
                    self._routes[route_info.route_key] = route_info
                    results['imported'] += 1
                
                # Sync to database
                await self.sync_to_database()
            
            results['info'] = f"Would import {len(import_data['routes'])} routes" if dry_run else f"Imported {results['imported']} routes"
            
        except Exception as e:
            results['errors'].append(f"Import failed: {e}")
            results['success'] = False
        
        return results
    
    def get_route(self, route_key: str) -> Optional[RouteInfo]:
        """Get route information by key"""
        return self._routes.get(route_key)
    
    def get_menu_tree(self) -> Dict[str, Any]:
        """Get current menu tree"""
        return self._menu_tree
    
    def get_routes_by_parent(self, parent_key: str) -> List[RouteInfo]:
        """Get all routes under a parent"""
        return [route for route in self._routes.values() if route.parent_route == parent_key]


# Global registry instance
route_registry = RouteRegistry()



