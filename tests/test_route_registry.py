"""
🌌 SarlakBot v3.0 - Route Registry Tests
Comprehensive tests for route registry system
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.route_registry import RouteRegistry, RouteInfo, RouteType
from src.core.menu_manager import MenuManager


class TestRouteRegistry:
    """Test Route Registry functionality"""
    
    @pytest.fixture
    def route_registry(self):
        """Create route registry instance"""
        registry = RouteRegistry()
        registry._routes.clear()  # Clear any existing routes
        return registry
    
    def test_route_registration(self, route_registry):
        """Test route registration with decorator"""
        
        @route_registry.register(
            route_key="test.route",
            button_text="Test Button",
            parent="test",
            order=1,
            route_type=RouteType.ACTION
        )
        def test_handler():
            return "test"
        
        # Check if route was registered
        assert "test.route" in route_registry._routes
        route_info = route_registry._routes["test.route"]
        
        assert route_info.route_key == "test.route"
        assert route_info.button_text == "Test Button"
        assert route_info.parent_route == "test"
        assert route_info.order_num == 1
        assert route_info.route_type == RouteType.ACTION
        assert route_info.handler_function == test_handler
    
    def test_duplicate_route_key(self, route_registry):
        """Test duplicate route key handling"""
        
        @route_registry.register("test.route", "Test Button")
        def handler1():
            return "test1"
        
        @route_registry.register("test.route", "Test Button 2")
        def handler2():
            return "test2"
        
        # Second registration should overwrite first
        assert route_registry._routes["test.route"].handler_function == handler2
    
    def test_route_validation(self, route_registry):
        """Test route validation"""
        
        # Add some test routes
        route_registry._routes["test.route1"] = RouteInfo(
            route_key="test.route1",
            handler_name="test.handler1",
            button_text="Test 1",
            handler_function=lambda: "test1"
        )
        
        route_registry._routes["test.route2"] = RouteInfo(
            route_key="test.route2",
            handler_name="test.handler2",
            button_text="Test 2",
            parent_route="test.route1",
            handler_function=lambda: "test2"
        )
        
        # Test validation
        results = asyncio.run(route_registry.validate_routes())
        
        assert "errors" in results
        assert "warnings" in results
        assert "info" in results
    
    def test_circular_reference_detection(self, route_registry):
        """Test circular reference detection"""
        
        # Create circular reference
        route_registry._routes["route1"] = RouteInfo(
            route_key="route1",
            handler_name="handler1",
            button_text="Route 1",
            parent_route="route2"
        )
        
        route_registry._routes["route2"] = RouteInfo(
            route_key="route2",
            handler_name="handler2",
            button_text="Route 2",
            parent_route="route1"
        )
        
        circular = route_registry._check_circular_references()
        assert len(circular) > 0
    
    def test_menu_depth_calculation(self, route_registry):
        """Test menu depth calculation"""
        
        # Create deep menu structure
        route_registry._routes["level1"] = RouteInfo(
            route_key="level1",
            handler_name="handler1",
            button_text="Level 1"
        )
        
        route_registry._routes["level2"] = RouteInfo(
            route_key="level2",
            handler_name="handler2",
            button_text="Level 2",
            parent_route="level1"
        )
        
        route_registry._routes["level3"] = RouteInfo(
            route_key="level3",
            handler_name="handler3",
            button_text="Level 3",
            parent_route="level2"
        )
        
        route_registry._routes["level4"] = RouteInfo(
            route_key="level4",
            handler_name="handler4",
            button_text="Level 4",
            parent_route="level3"
        )
        
        max_depth = route_registry._get_max_menu_depth()
        assert max_depth == 4
    
    def test_button_count_per_page(self, route_registry):
        """Test button count per page calculation"""
        
        # Add routes with same parent
        for i in range(10):
            route_registry._routes[f"route{i}"] = RouteInfo(
                route_key=f"route{i}",
                handler_name=f"handler{i}",
                button_text=f"Button {i}",
                parent_route="parent"
            )
        
        counts = route_registry._get_button_counts_per_page()
        assert counts["parent"] == 10
    
    @pytest.mark.asyncio
    async def test_export_routes(self, route_registry):
        """Test route export functionality"""
        
        # Add test route
        route_registry._routes["test.route"] = RouteInfo(
            route_key="test.route",
            handler_name="test.handler",
            button_text="Test Button",
            parent_route="test",
            order_num=1,
            route_type=RouteType.ACTION,
            metadata={"test": "value"}
        )
        
        export_data = await route_registry.export_routes()
        
        assert "version" in export_data
        assert "routes" in export_data
        assert len(export_data["routes"]) == 1
        
        route_data = export_data["routes"][0]
        assert route_data["route_key"] == "test.route"
        assert route_data["button_text"] == "Test Button"
        assert route_data["metadata"]["test"] == "value"
    
    @pytest.mark.asyncio
    async def test_import_routes(self, route_registry):
        """Test route import functionality"""
        
        import_data = {
            "version": "test_v1",
            "routes": [
                {
                    "route_key": "imported.route",
                    "handler_name": "imported.handler",
                    "button_text": "Imported Button",
                    "parent_route": None,
                    "order_num": 0,
                    "route_type": "menu",
                    "is_active": True,
                    "metadata": {}
                }
            ]
        }
        
        results = await route_registry.import_routes(import_data, dry_run=True)
        
        assert results["success"] is True
        assert results["imported"] == 0  # Dry run
        assert len(results["errors"]) == 0


class TestMenuManager:
    """Test Menu Manager functionality"""
    
    @pytest.fixture
    def menu_manager(self):
        """Create menu manager instance"""
        return MenuManager()
    
    @pytest.mark.asyncio
    async def test_get_menu(self, menu_manager):
        """Test menu generation"""
        
        # Mock database response
        mock_routes = [
            {
                "route_key": "test.route1",
                "button_text": "Test Button 1",
                "route_type": "action",
                "order_num": 1
            },
            {
                "route_key": "test.route2",
                "button_text": "Test Button 2",
                "route_type": "action",
                "order_num": 2
            }
        ]
        
        with patch.object(menu_manager, '_get_routes_by_parent', return_value=mock_routes):
            keyboard = await menu_manager.get_menu("test")
            
            assert keyboard is not None
            assert len(keyboard.inline_keyboard) >= 1  # At least one row
    
    @pytest.mark.asyncio
    async def test_breadcrumb_generation(self, menu_manager):
        """Test breadcrumb generation"""
        
        # Mock database response
        mock_route_info = {
            "route_key": "test.sub",
            "button_text": "Test Sub",
            "parent_route": "test"
        }
        
        mock_parent_info = {
            "route_key": "test",
            "button_text": "Test",
            "parent_route": None
        }
        
        with patch.object(menu_manager, '_get_routes_by_parent'):
            with patch('src.database.connection.db_manager.fetch_one') as mock_fetch:
                mock_fetch.side_effect = [mock_route_info, mock_parent_info, None]
                
                breadcrumb = await menu_manager.get_breadcrumb("test.sub")
                
                assert "Test" in breadcrumb
                assert "Test Sub" in breadcrumb
    
    @pytest.mark.asyncio
    async def test_cache_management(self, menu_manager):
        """Test cache management"""
        
        # Test cache clear
        await menu_manager.clear_cache()
        assert len(menu_manager._menu_cache) == 0
        
        # Test specific route cache clear
        menu_manager._menu_cache["test_123"] = "test_value"
        await menu_manager.clear_cache("test")
        assert "test_123" not in menu_manager._menu_cache


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_route_registry_with_database(self):
        """Test route registry with database integration"""
        
        # This would require a test database setup
        # For now, we'll mock the database interactions
        
        with patch('src.database.connection.db_manager') as mock_db:
            mock_db.fetch_all = AsyncMock(return_value=[])
            mock_db.execute = AsyncMock(return_value="OK")
            
            registry = RouteRegistry()
            
            # Add test route
            registry._routes["test.route"] = RouteInfo(
                route_key="test.route",
                handler_name="test.handler",
                button_text="Test Button"
            )
            
            # Test sync
            success = await registry.sync_to_database()
            assert success is True
    
    @pytest.mark.asyncio
    async def test_menu_manager_with_route_registry(self):
        """Test menu manager integration with route registry"""
        
        with patch('src.database.connection.db_manager') as mock_db:
            mock_db.fetch_all = AsyncMock(return_value=[])
            mock_db.fetch_one = AsyncMock(return_value=None)
            
            manager = MenuManager()
            
            # Test menu generation
            keyboard = await manager.get_menu("test")
            assert keyboard is None  # No routes found


if __name__ == "__main__":
    pytest.main([__file__])



