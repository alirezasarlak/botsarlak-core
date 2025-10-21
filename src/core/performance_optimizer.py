"""
🌌 SarlakBot v3.0 - Performance Optimizer
Scalability and performance optimizations
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import json

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PerformanceOptimizer:
    """
    🌌 Performance Optimizer
    Scalability and performance optimizations
    """
    
    def __init__(self):
        self.logger = logger
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._slow_queries: List[Dict[str, Any]] = []
        self._performance_metrics: Dict[str, List[float]] = {}
    
    def cache_result(self, ttl_seconds: int = 300):
        """
        Decorator to cache function results
        
        Args:
            ttl_seconds: Time to live in seconds
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
                
                # Check cache
                if cache_key in self._cache:
                    cache_time = self._cache_timestamps.get(cache_key)
                    if cache_time and datetime.now() - cache_time < timedelta(seconds=ttl_seconds):
                        self.logger.debug(f"Cache hit for {func.__name__}")
                        return self._cache[cache_key]
                
                # Execute function
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Cache result
                self._cache[cache_key] = result
                self._cache_timestamps[cache_key] = datetime.now()
                
                # Log performance
                self._log_performance(func.__name__, execution_time)
                
                return result
            
            return wrapper
        return decorator
    
    def monitor_performance(self, threshold_seconds: float = 1.0):
        """
        Decorator to monitor function performance
        
        Args:
            threshold_seconds: Threshold for slow operations
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log performance
                self._log_performance(func.__name__, execution_time)
                
                # Check for slow operations
                if execution_time > threshold_seconds:
                    self._log_slow_query(func.__name__, execution_time, args, kwargs)
                
                return result
            
            return wrapper
        return decorator
    
    def _log_performance(self, function_name: str, execution_time: float):
        """Log performance metrics"""
        try:
            if function_name not in self._performance_metrics:
                self._performance_metrics[function_name] = []
            
            self._performance_metrics[function_name].append(execution_time)
            
            # Keep only last 100 measurements
            if len(self._performance_metrics[function_name]) > 100:
                self._performance_metrics[function_name] = self._performance_metrics[function_name][-100:]
            
        except Exception as e:
            self.logger.error(f"Failed to log performance: {e}")
    
    def _log_slow_query(self, function_name: str, execution_time: float, args: tuple, kwargs: dict):
        """Log slow queries"""
        try:
            slow_query = {
                "function_name": function_name,
                "execution_time": execution_time,
                "args": str(args)[:200],  # Truncate long args
                "kwargs": str(kwargs)[:200],  # Truncate long kwargs
                "timestamp": datetime.now().isoformat()
            }
            
            self._slow_queries.append(slow_query)
            
            # Keep only last 50 slow queries
            if len(self._slow_queries) > 50:
                self._slow_queries = self._slow_queries[-50:]
            
            self.logger.warning(f"Slow operation: {function_name} took {execution_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to log slow query: {e}")
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            summary = {
                "cache_stats": {
                    "total_cached_items": len(self._cache),
                    "cache_hit_ratio": self._calculate_cache_hit_ratio()
                },
                "performance_metrics": {},
                "slow_queries": self._slow_queries[-10:],  # Last 10 slow queries
                "generated_at": datetime.now().isoformat()
            }
            
            # Calculate performance metrics
            for function_name, times in self._performance_metrics.items():
                if times:
                    summary["performance_metrics"][function_name] = {
                        "avg_time": sum(times) / len(times),
                        "min_time": min(times),
                        "max_time": max(times),
                        "total_calls": len(times),
                        "recent_avg": sum(times[-10:]) / min(len(times), 10) if times else 0
                    }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return {}
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        try:
            # This is a simplified calculation
            # In production, you'd track actual hits vs misses
            total_items = len(self._cache)
            if total_items == 0:
                return 0.0
            
            # Estimate based on cache age
            now = datetime.now()
            recent_items = sum(
                1 for timestamp in self._cache_timestamps.values()
                if now - timestamp < timedelta(minutes=5)
            )
            
            return recent_items / total_items if total_items > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to calculate cache hit ratio: {e}")
            return 0.0
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache"""
        try:
            if pattern:
                # Clear specific pattern
                keys_to_remove = [key for key in self._cache.keys() if pattern in key]
                for key in keys_to_remove:
                    del self._cache[key]
                    del self._cache_timestamps[key]
                
                self.logger.info(f"Cleared {len(keys_to_remove)} cache entries matching '{pattern}'")
            else:
                # Clear all cache
                self._cache.clear()
                self._cache_timestamps.clear()
                self.logger.info("Cleared all cache entries")
                
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
    
    async def optimize_database_queries(self) -> Dict[str, Any]:
        """Analyze and optimize database queries"""
        try:
            # Get slow queries from database
            slow_queries = await db_manager.fetch_all("""
                SELECT 
                    query,
                    mean_time,
                    calls,
                    total_time
                FROM pg_stat_statements 
                WHERE mean_time > 100  -- Queries taking more than 100ms on average
                ORDER BY mean_time DESC
                LIMIT 10
            """)
            
            # Get table statistics
            table_stats = await db_manager.fetch_all("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
                LIMIT 10
            """)
            
            # Get index usage
            index_usage = await db_manager.fetch_all("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                WHERE idx_scan > 0
                ORDER BY idx_scan DESC
                LIMIT 10
            """)
            
            return {
                "slow_queries": slow_queries,
                "table_stats": table_stats,
                "index_usage": index_usage,
                "optimization_suggestions": self._generate_optimization_suggestions(slow_queries, table_stats, index_usage)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to optimize database queries: {e}")
            return {}
    
    def _generate_optimization_suggestions(self, slow_queries: List[Dict], table_stats: List[Dict], index_usage: List[Dict]) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        try:
            # Analyze slow queries
            for query in slow_queries:
                if "SELECT" in query.get("query", ""):
                    if "ORDER BY" in query.get("query", "") and "LIMIT" not in query.get("query", ""):
                        suggestions.append("Consider adding LIMIT to queries with ORDER BY")
                    
                    if "WHERE" not in query.get("query", ""):
                        suggestions.append("Consider adding WHERE clauses to reduce result set")
            
            # Analyze table stats
            for table in table_stats:
                dead_ratio = table.get("dead_tuples", 0) / max(table.get("live_tuples", 1), 1)
                if dead_ratio > 0.1:  # More than 10% dead tuples
                    suggestions.append(f"Consider VACUUM on table {table.get('tablename')} (dead tuple ratio: {dead_ratio:.2%})")
            
            # Analyze index usage
            unused_indexes = [idx for idx in index_usage if idx.get("scans", 0) == 0]
            if unused_indexes:
                suggestions.append(f"Found {len(unused_indexes)} unused indexes - consider dropping them")
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization suggestions: {e}")
        
        return suggestions
    
    async def run_database_maintenance(self) -> Dict[str, Any]:
        """Run database maintenance tasks"""
        try:
            maintenance_results = {}
            
            # Analyze tables
            self.logger.info("Running ANALYZE on all tables...")
            await db_manager.execute("ANALYZE")
            maintenance_results["analyze"] = "completed"
            
            # Vacuum tables with high dead tuple ratio
            tables_to_vacuum = await db_manager.fetch_all("""
                SELECT tablename 
                FROM pg_stat_user_tables 
                WHERE n_dead_tup > n_live_tup * 0.1
            """)
            
            for table in tables_to_vacuum:
                table_name = table["tablename"]
                self.logger.info(f"Running VACUUM on table {table_name}...")
                await db_manager.execute(f"VACUUM {table_name}")
                maintenance_results[f"vacuum_{table_name}"] = "completed"
            
            # Update statistics
            self.logger.info("Updating database statistics...")
            await db_manager.execute("ANALYZE")
            maintenance_results["statistics_update"] = "completed"
            
            return maintenance_results
            
        except Exception as e:
            self.logger.error(f"Database maintenance failed: {e}")
            return {"error": str(e)}
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # Database connection pool stats
            pool_stats = {
                "size": db_manager.pool.get_size() if db_manager.pool else 0,
                "idle_size": db_manager.pool.get_idle_size() if db_manager.pool else 0,
                "max_size": db_manager.pool.get_max_size() if db_manager.pool else 0
            }
            
            # Cache stats
            cache_stats = {
                "total_items": len(self._cache),
                "memory_usage_estimate": len(str(self._cache))  # Rough estimate
            }
            
            # Performance metrics
            performance_summary = await self.get_performance_summary()
            
            return {
                "database_pool": pool_stats,
                "cache": cache_stats,
                "performance": performance_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()



