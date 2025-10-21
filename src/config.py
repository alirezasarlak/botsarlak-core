"""
🌌 SarlakBot v3.0 - Configuration Management
Gen-Z Cosmic Study Journey Configuration
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Version constants
VERSION = os.getenv("BOT_VERSION", "v2.4.0-profile-gamification")
LAST_UPDATE = os.getenv("LAST_UPDATE", "2025-10-18")
FEATURE_ONBOARDING_V1 = os.getenv("FEATURE_ONBOARDING_V1", "true").lower() == "true"
FEATURE_PROFILE_V1 = os.getenv("FEATURE_PROFILE_V1", "true").lower() == "true"
FEATURE_GAMIFICATION_V1 = os.getenv("FEATURE_GAMIFICATION_V1", "true").lower() == "true"
FEATURE_REPORT_V1 = os.getenv("FEATURE_REPORT_V1", "true").lower() == "true"
FEATURE_LEAGUE_V1 = os.getenv("FEATURE_LEAGUE_V1", "true").lower() == "true"
FEATURE_ANTI_FRAUD_V1 = os.getenv("FEATURE_ANTI_FRAUD_V1", "true").lower() == "true"
FEATURE_AUTO_TRACKING_V1 = os.getenv("FEATURE_AUTO_TRACKING_V1", "true").lower() == "true"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = os.getenv("DB_HOST", "127.0.0.1")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "botsarlak")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASS", "ali123123")
    
    @property
    def connection_string(self) -> str:
        """Get database connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class BotConfig:
    """Bot configuration"""
    token: str = os.getenv("BOT_TOKEN", "")
    admin_id: int = int(os.getenv("ADMIN_ID", "694245594"))
    required_channel: str = os.getenv("REQUIRED_CHANNEL", "@sarlak_academy")
    
    # Social links
    youtube_url: str = os.getenv("YOUTUBE_URL", "https://www.youtube.com/@SarlakAcademy")
    site_url: str = os.getenv("SITE_URL", "https://sarlak.academy")
    instagram_url: str = os.getenv("INSTAGRAM_URL", "https://instagram.com/Sarlak.academy")
    telegram_channel_url: str = os.getenv("TELEGRAM_CHANNEL_URL", "https://t.me/Sarlak_academy")


@dataclass
class FeatureFlags:
    """Feature flags for modular development"""
    onboarding_v1: bool = os.getenv("FEATURE_ONBOARDING_V1", "true").lower() == "true"
    profile_v1: bool = os.getenv("FEATURE_PROFILE_V1", "true").lower() == "true"
    gamification_v1: bool = os.getenv("FEATURE_GAMIFICATION_V1", "true").lower() == "true"
    report_v1: bool = os.getenv("FEATURE_REPORT_V1", "true").lower() == "true"
    league_v1: bool = os.getenv("FEATURE_LEAGUE_V1", "true").lower() == "true"
    anti_fraud_v1: bool = os.getenv("FEATURE_ANTI_FRAUD_V1", "true").lower() == "true"
    auto_tracking_v1: bool = os.getenv("FEATURE_AUTO_TRACKING_V1", "true").lower() == "true"
    motivation_v1: bool = os.getenv("FEATURE_MOTIVATION_V1", "true").lower() == "true"
    competition_v1: bool = os.getenv("FEATURE_COMPETITION_V1", "true").lower() == "true"
    store_v1: bool = os.getenv("FEATURE_STORE_V1", "true").lower() == "true"


@dataclass
class MonitoringConfig:
    """Monitoring and analytics configuration"""
    telemtry_enabled: bool = os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    health_check_port: int = int(os.getenv("HEALTH_CHECK_PORT", "8080"))


@dataclass
class AIConfig:
    """AI integration configuration"""
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")


@dataclass
class ServerConfig:
    """Server deployment configuration"""
    user: str = os.getenv("SERVER_USER", "ali")
    ip: str = os.getenv("SERVER_IP", "163.5.94.227")
    path: str = os.getenv("SERVER_PATH", "/home/ali/botsarlak")


class Config:
    """
    🌌 Main Configuration Class
    Centralized configuration management for SarlakBot v3.0
    """
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.bot = BotConfig()
        self.features = FeatureFlags()
        self.monitoring = MonitoringConfig()
        self.ai = AIConfig()
        self.server = ServerConfig()
        
        # Validate critical configurations
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate critical configuration values"""
        if not self.bot.token:
            print("⚠️ Warning: BOT_TOKEN not set, using default for testing")
            self.bot.token = "test_token"
        
        if not self.database.password:
            raise ValueError("Database password is required")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENVIRONMENT", "development") == "production"


# Global configuration instance
config = Config()
