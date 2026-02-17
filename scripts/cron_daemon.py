#!/usr/bin/env python3
"""
Fractal Daily Cron Daemon
Runs daily job at UTC 00:10
"""

import time
import subprocess
import os
from datetime import datetime, timezone

CRON_HOUR = 0
CRON_MINUTE = 10
SCRIPT_PATH = "/app/scripts/daily_cron.sh"

def get_next_run():
    """Calculate next run time"""
    now = datetime.now(timezone.utc)
    target = now.replace(hour=CRON_HOUR, minute=CRON_MINUTE, second=0, microsecond=0)
    
    if now >= target:
        # Already passed today, run tomorrow
        from datetime import timedelta
        target = target + timedelta(days=1)
    
    return target

def main():
    print(f"[CronDaemon] Started. Schedule: {CRON_HOUR:02d}:{CRON_MINUTE:02d} UTC daily")
    
    last_run_date = None
    
    while True:
        now = datetime.now(timezone.utc)
        today = now.date()
        
        # Check if it's time to run (and haven't run today)
        if (now.hour == CRON_HOUR and 
            now.minute >= CRON_MINUTE and 
            last_run_date != today):
            
            print(f"[CronDaemon] {now.isoformat()} - Triggering daily job...")
            
            try:
                result = subprocess.run(
                    [SCRIPT_PATH],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                print(f"[CronDaemon] Job completed. Return code: {result.returncode}")
                if result.stdout:
                    print(f"[CronDaemon] stdout: {result.stdout[:500]}")
                if result.stderr:
                    print(f"[CronDaemon] stderr: {result.stderr[:500]}")
            except Exception as e:
                print(f"[CronDaemon] Error: {e}")
            
            last_run_date = today
        
        # Sleep for 30 seconds between checks
        time.sleep(30)

if __name__ == "__main__":
    main()
