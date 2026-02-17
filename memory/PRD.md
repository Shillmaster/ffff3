# Fractal Research Terminal — Production Infrastructure

## Original Problem Statement
Production-ready Fractal система с:
- Daily Cron Job для сбора forward-truth данных
- Telegram Admin Alerts (только risk-control, без маркетинга)
- Жёсткий governance контроль (manual only, no auto-promotion)
- Contract Freeze Pack v1.0.0

Source: https://github.com/Shillmaster/ddddd

## Architecture
- **Backend:** FastAPI proxy (port 8001) → TypeScript Fastify (port 8002)
- **Frontend:** React + TailwindCSS + Canvas API
- **Database:** MongoDB (local, fractal_dev)
- **Process Manager:** Supervisor
- **Notifications:** Telegram Bot @F_FOMO_bot (admin only)

## Contract Status

| Property | Value |
|----------|-------|
| **Version** | v2.1.0 |
| **Status** | **FROZEN** |
| **Contract Hash** | 44de469209e4982d |
| **Symbol** | BTC only |
| **Horizons** | 7d / 14d / 30d |
| **Auto-promotion** | DISABLED |
| **Auto-training** | DISABLED |

## ✅ BLOCK A — Contract Freeze Pack v1.0.0

### Files Created
```
/modules/fractal/contracts/
├── fractal.signal.contract.ts   # FractalSignalContract (frozen)
├── fractal.signal.validator.ts  # Runtime validation
└── index.ts

/modules/fractal/freeze/
├── fractal.freeze.config.ts     # Freeze configuration
├── fractal.freeze.guard.ts      # Guards and middleware
├── fractal.freeze.stamp.ts      # Audit stamp
├── fractal.freeze.routes.ts     # Admin endpoints
└── index.ts
```

### API Endpoints
- `GET /admin/freeze-status` — Quick freeze check
- `GET /admin/freeze-stamp` — Full audit stamp

### Guarantees
- `noAutoPromotion: true`
- `noAutoTraining: true`
- `manualGovernanceOnly: true`
- `symbol: BTC`
- `horizons: [7, 14, 30]`

## Production Infrastructure

### Daily Cron Loop (UTC 00:10)
```
DAILY CRON
    ↓
1. Snapshot Writer (BTC)
2. Outcome Resolver (7/14/30 matured)
3. Forward Equity Rebuild
4. Audit Log
    ↓
IF event → Telegram Admin Alert
```

### Telegram Notification Policy
| Level | Trigger | When |
|-------|---------|------|
| CRITICAL | HALT/PROTECTION mode | Immediate |
| ALERT | Guard warning | Immediate |
| INFO | Daily report | Daily |
| MILESTONE | 30+ resolved | Once |

### Cron Setup
```bash
10 0 * * * curl -X POST "https://DOMAIN/api/fractal/v2.1/admin/jobs/daily-run-tg" \
  -H "Authorization: Bearer FRACTAL_CRON_SECRET" -d '{"symbol":"BTC"}'
```

## Environment Variables

```bash
# Core
MONGO_URL=mongodb://localhost:27017/fractal_dev
FRACTAL_ONLY=1
FRACTAL_ENABLED=true

# Contract Freeze
FRACTAL_FROZEN=true
FRACTAL_VERSION=v2.1.0
FRACTAL_FROZEN_AT=2026-02-17T18:00:00Z

# Telegram
TG_BOT_TOKEN=8317741262:xxx
TG_ADMIN_CHAT_ID=577782582

# Cron
FRACTAL_CRON_SECRET=xxx
```

## Documentation

Created institutional docs:
- `/modules/fractal/README.md` — Overview
- `/modules/fractal/CONTRACT.md` — Signal contract spec
- `/modules/fractal/GOVERNANCE.md` — Governance policy
- `/modules/fractal/OPERATIONS.md` — Ops procedures

## Next Blocks

### ✅ BLOCK B — Module Isolation Audit (COMPLETED 2026-02-17)
- [x] FractalHostDeps interface (`/isolation/fractal.host.deps.ts`)
- [x] Forbidden imports registry (`/isolation/forbidden.imports.ts`)
- [x] Fail containment wrapper (`/isolation/fail.containment.ts`)
- [x] Linting script (`scripts/check-fractal-isolation.ts`)
- [x] Isolation tests (15 tests PASSED)

### ✅ BLOCK 58 — Hierarchical Resolver (COMPLETED 2026-02-17)
- [x] HierarchicalResolverService (Bias + Timing + Final)
- [x] Horizon config (7d/14d/30d/90d/180d/365d)
- [x] Multi-signal endpoint (GET /api/fractal/v2.1/multi-signal)
- [x] 11 vitest tests PASSED

### ✅ BLOCK 59 — Extended Horizons (COMPLETED 2026-02-17)
- [x] 90d/180d/365d horizon support
- [x] Regime endpoint (GET /api/fractal/v2.1/regime)
- [x] Global Bias calculation (long-horizon dominance)

### ✅ PHASE 2 P0.1-P0.4 — Multi-Layer Regime System (COMPLETED 2026-02-17)
- [x] P0.1: Terminal Aggregator endpoint (one request → entire terminal)
- [x] P0.2: HorizonSelector + HorizonMatrix components
- [x] P0.3: GlobalStructureBar component
- [x] P0.4: useFractalTerminal hook

### ✅ BLOCK E — Telegram Admin Alerts + Cron Hardening (COMPLETED 2026-02-17)
- [x] TelegramHardenedService (rate limit, retry, deduplication)
- [x] CronHardeningService (lock, idempotency, timeout protection)
- [x] Extended alert templates (8 new message types)
- [x] Hardened OPS routes (6 new endpoints)
- [x] 19 vitest tests PASSED

### ✅ BLOCK 59.2 — Decision Kernel (P1.1 + P1.2) (COMPLETED 2026-02-17)
- [x] P1.1: Consensus Index (`consensus.index.ts`)
  - Tier weights: STRUCTURE 40%, TACTICAL 35%, TIMING 25%
  - Blocker penalties: LOW_CONFIDENCE, HIGH_ENTROPY, HIGH_TAIL_RISK
  - consensusToMultiplier() for dynamic sizing
  - 18 vitest tests PASSED
- [x] P1.2: Conflict Resolver Policy (`conflict.policy.ts`)
  - Conflict levels: NONE, MINOR, MODERATE, MAJOR, SEVERE
  - Resolution modes: TREND_FOLLOW, COUNTER_TREND, WAIT
  - Sizing penalties: 0%, 10%, 25%, 50%, 75%
  - Tier summaries and divergence scoring
  - 19 vitest tests PASSED
- [x] API Integration: `/api/fractal/v2.1/terminal` returns `decisionKernel.consensus` + `decisionKernel.conflict`

### BLOCK D — Full Documentation Pack
- [ ] ARCHITECTURE.md
- [ ] SECURITY.md
- [ ] Integration checklist

## Timeline

| Timeframe | Status |
|-----------|--------|
| Day 1-6 | Daily reports, resolvedCount = 0 |
| Day 7 | First 7d signals resolved |
| Day 14 | Forward equity forming |
| Day 30 | **MILESTONE** — Governance enabled |
| Day 90 | Promotion decisions possible |

## System Status

```
✅ BTC only
✅ Frozen horizons 7/14/30
✅ No auto-promotion
✅ Manual governance
✅ Daily cron ACTIVE
✅ Telegram alerts ACTIVE
✅ Contract FROZEN (v2.1.0)
✅ Forward equity accumulating
✅ BLOCK B: Module Isolation COMPLETE
✅ BLOCK E: Telegram + Cron Hardening COMPLETE
```

## BLOCK B Files Created

```
/modules/fractal/isolation/
├── fractal.host.deps.ts      # FractalHostDeps interface + defaults
├── fail.containment.ts       # Safe HOLD wrapper on errors
├── forbidden.imports.ts      # Import rules registry
├── index.ts                  # Public exports
└── __tests__/
    └── isolation.test.ts     # 15 vitest tests

/backend/scripts/
└── check-fractal-isolation.ts  # Linting script (npx tsx)
```

## BLOCK E Files Created

```
/modules/fractal/ops/
├── telegram.hardened.ts       # Rate limit + retry + deduplication
├── cron.hardening.ts          # Lock + idempotency + timeout
├── telegram.alerts.extended.ts # 8 new alert templates
├── ops.hardened.routes.ts     # 6 new admin endpoints
└── __tests__/
    ├── telegram.hardened.test.ts  # 8 tests
    └── cron.hardening.test.ts     # 11 tests
```

## BLOCK E API Endpoints

```
GET  /admin/telegram/health       # TG service health
GET  /admin/telegram/stats        # Sending statistics
POST /admin/telegram/test-hardened # Test hardened sender
GET  /admin/cron/status           # Cron locks & stats
GET  /admin/cron/history          # Execution history
POST /admin/jobs/daily-run-hardened # Hardened daily job
POST /admin/notify/startup        # Startup notification
```

**Status:** READY FOR LIVE
