-- Route Registry System Tables
-- The Living Map - Self-healing route management

-- ==================== ROUTES TABLE ====================
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    route_key VARCHAR(255) UNIQUE NOT NULL,
    handler_name VARCHAR(500) NOT NULL,
    button_text VARCHAR(255) NOT NULL,
    parent_route VARCHAR(255),
    order_num INTEGER DEFAULT 0,
    route_type VARCHAR(50) DEFAULT 'menu',
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Foreign key constraint for parent_route
    FOREIGN KEY (parent_route) REFERENCES routes(route_key) ON DELETE SET NULL
);

-- ==================== MENUS TABLE ====================
CREATE TABLE IF NOT EXISTS menus (
    id SERIAL PRIMARY KEY,
    menu_name VARCHAR(255) UNIQUE NOT NULL,
    menu_json JSONB NOT NULL,
    version VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== ROUTE HISTORY TABLE ====================
CREATE TABLE IF NOT EXISTS route_history (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    route_key VARCHAR(255),
    payload JSONB DEFAULT '{}',
    admin_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== INDEXES ====================
-- Routes table indexes
CREATE INDEX IF NOT EXISTS idx_routes_route_key ON routes(route_key);
CREATE INDEX IF NOT EXISTS idx_routes_parent_route ON routes(parent_route);
CREATE INDEX IF NOT EXISTS idx_routes_is_active ON routes(is_active);
CREATE INDEX IF NOT EXISTS idx_routes_order ON routes(parent_route, order_num);

-- Menus table indexes
CREATE INDEX IF NOT EXISTS idx_menus_menu_name ON menus(menu_name);
CREATE INDEX IF NOT EXISTS idx_menus_version ON menus(version);

-- Route history indexes
CREATE INDEX IF NOT EXISTS idx_route_history_action ON route_history(action);
CREATE INDEX IF NOT EXISTS idx_route_history_route_key ON route_history(route_key);
CREATE INDEX IF NOT EXISTS idx_route_history_created_at ON route_history(created_at);

-- ==================== TRIGGERS ====================
-- Update timestamp trigger for routes
CREATE OR REPLACE FUNCTION update_routes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_routes_updated_at
    BEFORE UPDATE ON routes
    FOR EACH ROW
    EXECUTE FUNCTION update_routes_updated_at();

-- Update timestamp trigger for menus
CREATE OR REPLACE FUNCTION update_menus_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_menus_updated_at
    BEFORE UPDATE ON menus
    FOR EACH ROW
    EXECUTE FUNCTION update_menus_updated_at();

-- ==================== INITIAL ROUTES ====================
-- Insert basic menu structure
INSERT INTO routes (route_key, handler_name, button_text, parent_route, order_num, route_type, is_active) VALUES
('main', 'main_menu', '🏠 منوی اصلی', NULL, 0, 'menu', TRUE),
('study', 'study_menu', '📚 مطالعه', 'main', 1, 'menu', TRUE),
('profile', 'profile_menu', '🪐 پروفایل', 'main', 2, 'menu', TRUE),
('motivation', 'motivation_menu', '🌟 انگیزه', 'main', 3, 'menu', TRUE),
('competition', 'competition_menu', '☄️ رقابت', 'main', 4, 'menu', TRUE),
('store', 'store_menu', '🛍️ فروشگاه', 'main', 5, 'menu', TRUE),
('compass', 'compass_menu', '🧭 قطب‌نما', 'main', 6, 'menu', TRUE),
('settings', 'settings_menu', '⚙️ تنظیمات', 'main', 7, 'menu', TRUE),
('help', 'help_menu', '❓ راهنما', 'main', 8, 'menu', TRUE)
ON CONFLICT (route_key) DO NOTHING;

-- Study submenu
INSERT INTO routes (route_key, handler_name, button_text, parent_route, order_num, route_type, is_active) VALUES
('study.report', 'study_report', '📘 گزارش مطالعه', 'study', 1, 'action', TRUE),
('study.session', 'study_session', '⏱️ جلسه مطالعه', 'study', 2, 'action', TRUE),
('study.progress', 'study_progress', '📊 پیشرفت', 'study', 3, 'action', TRUE),
('study.goals', 'study_goals', '🎯 اهداف', 'study', 4, 'action', TRUE)
ON CONFLICT (route_key) DO NOTHING;

-- Profile submenu
INSERT INTO routes (route_key, handler_name, button_text, parent_route, order_num, route_type, is_active) VALUES
('profile.view', 'profile_view', '👤 مشاهده پروفایل', 'profile', 1, 'action', TRUE),
('profile.edit', 'profile_edit', '✏️ ویرایش پروفایل', 'profile', 2, 'action', TRUE),
('profile.stats', 'profile_stats', '📈 آمار', 'profile', 3, 'action', TRUE),
('profile.achievements', 'profile_achievements', '🏆 دستاوردها', 'profile', 4, 'action', TRUE)
ON CONFLICT (route_key) DO NOTHING;

-- ==================== INITIAL MENU ====================
INSERT INTO menus (menu_name, menu_json, version) VALUES (
    'main_menu',
    '{
        "route_key": "root",
        "children": [
            {
                "route_key": "main",
                "button_text": "🏠 منوی اصلی",
                "route_type": "menu",
                "children": [
                    {
                        "route_key": "study",
                        "button_text": "📚 مطالعه",
                        "route_type": "menu",
                        "children": [
                            {
                                "route_key": "study.report",
                                "button_text": "📘 گزارش مطالعه",
                                "route_type": "action",
                                "children": []
                            },
                            {
                                "route_key": "study.session",
                                "button_text": "⏱️ جلسه مطالعه",
                                "route_type": "action",
                                "children": []
                            },
                            {
                                "route_key": "study.progress",
                                "button_text": "📊 پیشرفت",
                                "route_type": "action",
                                "children": []
                            },
                            {
                                "route_key": "study.goals",
                                "button_text": "🎯 اهداف",
                                "route_type": "action",
                                "children": []
                            }
                        ]
                    },
                    {
                        "route_key": "profile",
                        "button_text": "🪐 پروفایل",
                        "route_type": "menu",
                        "children": [
                            {
                                "route_key": "profile.view",
                                "button_text": "👤 مشاهده پروفایل",
                                "route_type": "action",
                                "children": []
                            },
                            {
                                "route_key": "profile.edit",
                                "button_text": "✏️ ویرایش پروفایل",
                                "route_type": "action",
                                "children": []
                            },
                            {
                                "route_key": "profile.stats",
                                "button_text": "📈 آمار",
                                "route_type": "action",
                                "children": []
                            },
                            {
                                "route_key": "profile.achievements",
                                "button_text": "🏆 دستاوردها",
                                "route_type": "action",
                                "children": []
                            }
                        ]
                    },
                    {
                        "route_key": "motivation",
                        "button_text": "🌟 انگیزه",
                        "route_type": "menu",
                        "children": []
                    },
                    {
                        "route_key": "competition",
                        "button_text": "☄️ رقابت",
                        "route_type": "menu",
                        "children": []
                    },
                    {
                        "route_key": "store",
                        "button_text": "🛍️ فروشگاه",
                        "route_type": "menu",
                        "children": []
                    },
                    {
                        "route_key": "compass",
                        "button_text": "🧭 قطب‌نما",
                        "route_type": "menu",
                        "children": []
                    },
                    {
                        "route_key": "settings",
                        "button_text": "⚙️ تنظیمات",
                        "route_type": "menu",
                        "children": []
                    },
                    {
                        "route_key": "help",
                        "button_text": "❓ راهنما",
                        "route_type": "menu",
                        "children": []
                    }
                ]
            }
        ]
    }',
    'initial_v1'
) ON CONFLICT (menu_name) DO NOTHING;



