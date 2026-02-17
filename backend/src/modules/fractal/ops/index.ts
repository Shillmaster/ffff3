/**
 * FRACTAL OPS — Operations Module Index
 * 
 * Production infrastructure:
 * - Telegram notifications (admin only)
 * - Cron authentication
 * - Daily job orchestration
 */

export { tgSendMessage, getTelegramConfig } from './telegram.notifier.js';
export {
  buildDailyReport,
  buildCriticalAlert,
  buildMilestone30Resolved,
  buildTestMessage,
  buildJobFailedAlert
} from './telegram.messages.js';
export { requireCronAuth, cronAuthHook, hasCronAuth } from './cron.auth.js';
export { runDailyWithTelegram } from './daily-run-telegram.service.js';
