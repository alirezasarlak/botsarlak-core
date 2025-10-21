#!/usr/bin/env python3
"""
Deploy Q&A System to Production Server
"""

import subprocess
import time
import sys

def run_command(cmd, description):
    """Run command and return result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    """Main deployment process"""
    print("🚀 Starting Q&A System Deployment...")
    
    # Step 1: Sync code to server
    if not run_command(
        "rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' . botsarlak-server:/home/ali/botsarlak/",
        "Syncing code to server"
    ):
        print("❌ Code sync failed")
        return False
    
    # Step 2: Wait for connection
    print("⏳ Waiting for server connection...")
    time.sleep(10)
    
    # Step 3: Run migration
    if not run_command(
        "ssh botsarlak-server 'cd /home/ali/botsarlak && source .venv/bin/activate && PGPASSWORD=ali123123 psql -h localhost -U postgres -d sarlak_academy -f migrations/versions/012_qa_system.sql'",
        "Running database migration"
    ):
        print("❌ Migration failed")
        return False
    
    # Step 4: Install dependencies
    if not run_command(
        "ssh botsarlak-server 'cd /home/ali/botsarlak && source .venv/bin/activate && pip install openai'",
        "Installing OpenAI dependency"
    ):
        print("❌ Dependency installation failed")
        return False
    
    # Step 5: Wait for connection
    print("⏳ Waiting for server connection...")
    time.sleep(10)
    
    # Step 6: Restart service
    if not run_command(
        "ssh botsarlak-server 'sudo systemctl restart botsarlak'",
        "Restarting bot service"
    ):
        print("❌ Service restart failed")
        return False
    
    # Step 7: Wait and check status
    print("⏳ Waiting for service to start...")
    time.sleep(15)
    
    if not run_command(
        "ssh botsarlak-server 'sudo systemctl status botsarlak'",
        "Checking service status"
    ):
        print("❌ Service status check failed")
        return False
    
    print("🎉 Q&A System deployment completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
