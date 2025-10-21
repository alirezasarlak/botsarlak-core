#!/usr/bin/env python3
"""
🌌 SarlakBot v3.0 - Route Synchronization Script
Synchronizes routes from code to database
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.core.route_registry import route_registry
from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def sync_routes():
    """Main synchronization function"""
    try:
        logger.info("🚀 Starting route synchronization...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Sync routes to database
        success = await route_registry.sync_to_database()
        
        if success:
            logger.info("✅ Route synchronization completed successfully")
            
            # Validate routes
            validation_results = await route_registry.validate_routes()
            
            if validation_results['errors']:
                logger.error("❌ Validation errors found:")
                for error in validation_results['errors']:
                    logger.error(f"  - {error}")
                return False
            
            if validation_results['warnings']:
                logger.warning("⚠️ Validation warnings:")
                for warning in validation_results['warnings']:
                    logger.warning(f"  - {warning}")
            
            if validation_results['info']:
                logger.info("ℹ️ Validation info:")
                for info in validation_results['info']:
                    logger.info(f"  - {info}")
            
            return True
        else:
            logger.error("❌ Route synchronization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Route synchronization error: {e}")
        return False
    finally:
        await db_manager.close()


async def validate_routes():
    """Validate routes without syncing"""
    try:
        logger.info("🔍 Validating routes...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Validate routes
        validation_results = await route_registry.validate_routes()
        
        # Print results
        if validation_results['errors']:
            logger.error("❌ Validation errors:")
            for error in validation_results['errors']:
                logger.error(f"  - {error}")
        
        if validation_results['warnings']:
            logger.warning("⚠️ Validation warnings:")
            for warning in validation_results['warnings']:
                logger.warning(f"  - {warning}")
        
        if validation_results['info']:
            logger.info("ℹ️ Validation info:")
            for info in validation_results['info']:
                logger.info(f"  - {info}")
        
        success = len(validation_results['errors']) == 0
        return success
        
    except Exception as e:
        logger.error(f"❌ Route validation error: {e}")
        return False
    finally:
        await db_manager.close()


async def export_routes():
    """Export routes to JSON"""
    try:
        logger.info("📤 Exporting routes...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Export routes
        export_data = await route_registry.export_routes()
        
        if export_data:
            # Save to file
            import json
            output_file = "routes_export.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Routes exported to {output_file}")
            return True
        else:
            logger.error("❌ Failed to export routes")
            return False
            
    except Exception as e:
        logger.error(f"❌ Route export error: {e}")
        return False
    finally:
        await db_manager.close()


async def import_routes(file_path: str, dry_run: bool = True):
    """Import routes from JSON"""
    try:
        logger.info(f"📥 Importing routes from {file_path}...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Read import file
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # Import routes
        results = await route_registry.import_routes(import_data, dry_run)
        
        if results['success']:
            logger.info(f"✅ Import completed: {results['info']}")
            
            if results['errors']:
                logger.error("❌ Import errors:")
                for error in results['errors']:
                    logger.error(f"  - {error}")
            
            if results['warnings']:
                logger.warning("⚠️ Import warnings:")
                for warning in results['warnings']:
                    logger.warning(f"  - {warning}")
            
            return True
        else:
            logger.error("❌ Import failed:")
            for error in results['errors']:
                logger.error(f"  - {error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Route import error: {e}")
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="SarlakBot Route Synchronization Tool")
    parser.add_argument("action", choices=["sync", "validate", "export", "import"],
                       help="Action to perform")
    parser.add_argument("--file", help="File path for import/export")
    parser.add_argument("--dry-run", action="store_true", help="Dry run for import")
    
    args = parser.parse_args()
    
    if args.action == "sync":
        success = await sync_routes()
    elif args.action == "validate":
        success = await validate_routes()
    elif args.action == "export":
        success = await export_routes()
    elif args.action == "import":
        if not args.file:
            logger.error("❌ --file argument required for import")
            sys.exit(1)
        success = await import_routes(args.file, args.dry_run)
    
    if success:
        print("✅ Operation completed successfully")
        sys.exit(0)
    else:
        print("❌ Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



