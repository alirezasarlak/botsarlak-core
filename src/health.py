"""
🌌 SarlakBot v3.0 - Health Check System
Professional health monitoring and metrics
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from src.config import config
from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Create FastAPI app for health checks
app = FastAPI(
    title="SarlakBot v3.0 Health API",
    description="Health monitoring and metrics for SarlakBot",
    version="3.0.0"
)


@app.get("/healthz")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for Kubernetes/Docker
    Returns 200 if healthy, 503 if unhealthy
    """
    try:
        # Check database health
        db_health = await db_manager.health_check()
        
        # Determine overall health
        is_healthy = db_health.get('status') == 'healthy'
        
        health_data = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'version': '3.0.0',
            'database': db_health,
            'features': {
                'onboarding': config.features.onboarding_v1,
                'profile': config.features.profile_v1,
                'report': config.features.report_v1,
                'motivation': config.features.motivation_v1,
                'competition': config.features.competition_v1,
                'store': config.features.store_v1
            }
        }
        
        if is_healthy:
            return health_data
        else:
            raise HTTPException(status_code=503, detail=health_data)
            
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        error_data = {
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }
        raise HTTPException(status_code=503, detail=error_data)


@app.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint
    Returns 200 if ready to serve traffic
    """
    try:
        # Check if database is ready
        await db_manager.fetch_value("SELECT 1")
        
        return {
            'status': 'ready',
            'timestamp': datetime.now().isoformat(),
            'version': '3.0.0'
        }
        
    except Exception as e:
        logger.error(f"❌ Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail={'status': 'not_ready', 'error': str(e)})


@app.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """
    Metrics endpoint for monitoring
    Returns system metrics and statistics
    """
    try:
        # Get user statistics
        total_users = await db_manager.fetch_value("SELECT COUNT(*) FROM users") or 0
        active_users = await db_manager.fetch_value("""
            SELECT COUNT(*) FROM users 
            WHERE last_activity > NOW() - INTERVAL '24 hours'
        """) or 0
        
        # Get study session statistics
        total_sessions = await db_manager.fetch_value("SELECT COUNT(*) FROM study_sessions") or 0
        today_sessions = await db_manager.fetch_value("""
            SELECT COUNT(*) FROM study_sessions 
            WHERE created_at > CURRENT_DATE
        """) or 0
        
        # Get database metrics
        db_health = await db_manager.health_check()
        
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '3.0.0',
            'users': {
                'total': total_users,
                'active_24h': active_users
            },
            'study_sessions': {
                'total': total_sessions,
                'today': today_sessions
            },
            'database': {
                'status': db_health.get('status'),
                'pool_size': db_health.get('pool_stats', {}).get('size', 0),
                'idle_size': db_health.get('pool_stats', {}).get('idle_size', 0)
            },
            'system': {
                'uptime': asyncio.get_event_loop().time(),
                'memory_usage': 'N/A',  # Would need psutil for real metrics
                'cpu_usage': 'N/A'
            }
        }
        
        return metrics_data
        
    except Exception as e:
        logger.error(f"❌ Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail={'error': str(e)})


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with basic info"""
    return {
        'name': 'SarlakBot v3.0 Health API',
        'version': '3.0.0',
        'description': 'Health monitoring and metrics for SarlakBot',
        'endpoints': {
            'health': '/healthz',
            'readiness': '/ready',
            'metrics': '/metrics'
        }
    }


async def start_health_server():
    """Start the health check server"""
    try:
        logger.info(f"🏥 Starting health check server on port {config.monitoring.health_check_port}")
        
        config_uvicorn = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8081,
            log_level="info",
            access_log=False
        )
        
        server = uvicorn.Server(config_uvicorn)
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Health server failed: {e}")
        raise


if __name__ == "__main__":
    # Run health server if called directly
    asyncio.run(start_health_server())
