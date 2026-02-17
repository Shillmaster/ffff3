#!/bin/bash
# Fractal Daily Cron Job - Production
# Schedule: 10 0 * * * (UTC 00:10)

BACKEND_URL="https://multi-layer-decision.preview.emergentagent.com"
CRON_SECRET="fractal_production_cron_secret_2024"
LOG_FILE="/var/log/fractal_cron.log"

echo "$(date -u '+%Y-%m-%d %H:%M:%S UTC') - Starting daily job..." >> $LOG_FILE

response=$(curl -sS -X POST "${BACKEND_URL}/api/fractal/v2.1/admin/jobs/daily-run-tg" \
  -H "Authorization: Bearer ${CRON_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC"}' 2>&1)

echo "$response" >> $LOG_FILE
echo "$(date -u '+%Y-%m-%d %H:%M:%S UTC') - Job completed" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE
