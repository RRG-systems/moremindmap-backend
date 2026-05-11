# THINK Memory System

Rocky's reasoning spine. SQLite-backed queryable history of bots, hypotheses, mutations, and decisions.

## Architecture

```
Arena (execution truth)
        ↓
    Events
        ↓
THINK Memory (interpreted history)
        ↓
Rocky (reasoning engine)
```

**Arena** owns execution metrics and real-time state.
**THINK Memory** stores compressed, decision-relevant history at state changes.
**Rocky** uses THINK Memory to answer 5 critical questions.

## Tables

### hypotheses
- `hypothesis_id` (PK)
- `title`, `description`
- `target_market`, `target_regime` (ranging | trending | high_vol | low_vol | mixed)
- `expected_behavior`, `failure_modes` (JSON array)
- `allowed_parameter_clusters` (JSON: entry, exit, hold, selectivity, size, concentration)
- `status` (testing | promising | weak | broken | retired)
- `supporting_bots` (JSON array of bot_ids currently testing this hypothesis)
- `strongest_bot_id` (best performer on this hypothesis)
- `notes_summary` (human-readable summary of hypothesis behavior)
- `created_at`, `updated_at`

### bots
- `bot_id` (PK)
- `parent_bot_id` (lineage)
- `generation` (how many ancestors)
- `hypothesis_id` (FK, what edge claim is this bot testing?)
- `creation_source` (manual | rocky_proposal | seed_agent | molt_feed)
- `created_by_mutation_id` (FK, which mutation spawned this?)
- `dna_json` (current parameters: entry_threshold, exit_threshold, hold_time, selectivity, trade_size, max_open_positions)
- `role` (active | baby | control | retired)
- `current_status` (testing | active | paused | failed | promoted | retired)
- `current_run_id` (which arena run?)
- `latest_metrics_json` (trades, flip_rate, shadow_pnl, divergence, drawdown, survival, trajectory, control_action)
- `created_at`, `retired_at`, `updated_at`

### mutations
- `mutation_id` (PK)
- `source_bot_id` (FK, what bot was mutated?)
- `resulting_bot_ids` (JSON array: 1 canonical + 10 variants = 11 total)
- `hypothesis_id` (FK)
- `source_proposal_id` (NULL if not from a Rocky proposal)
- `diagnosis` (what problem: "high flip rate", "weak exits", etc.)
- `mutation_type` (exit | selectivity | size | entry | hold | concentration)
- `parameter_changes` (JSON: {param: {before: X, after: Y}, ...})
- `rationale` (why this mutation was chosen)
- `expected_effect` (lower flip rate, lower drawdown, etc.)
- `result` (helped | hurt | inconclusive | pending)
- `result_summary` (brief explanation of result)
- `created_at`, `evaluated_at`

### decisions
- `decision_id` (PK)
- `related_bot_id` (FK)
- `related_hypothesis_id` (FK)
- `related_mutation_id` (FK)
- `source` (user | rocky | control_layer)
- `decision_type` (approve_proposal | reject_proposal | promote_bot | kill_bot | start_new_run | hold | switch | control_action)
- `context_snapshot` (JSON of key metrics at decision time)
- `reason` (why this decision was made)
- `outcome` (NULL initially; updated later with result)
- `timestamp`

## Setup

```bash
cd ~/.openclaw/workspace/molt
npm install sqlite3
node init-think-memory.js
```

## Usage

### Create a Hypothesis

```javascript
const memory = new THINKMemory();
await memory.init();

await memory.createHypothesis({
  hypothesis_id: 'hyp_meanrev_001',
  title: 'Short-term Mean Reversion (Low Vol)',
  description: 'Price reversals exist in low volatility regimes',
  target_market: 'BTC',
  target_regime: 'low_vol',
  expected_behavior: 'Quick reversal captures on -2% > -5% moves',
  failure_modes: ['regime change to trending', 'execution drag kills signal'],
  allowed_parameter_clusters: ['entry', 'selectivity', 'exit'],
  notes_summary: 'Initial testing'
});
```

### Spawn a Bot from a Hypothesis

```javascript
await memory.createBot({
  bot_id: 'bot_meanrev_001_gen1',
  hypothesis_id: 'hyp_meanrev_001',
  creation_source: 'manual',
  dna_json: {
    entry_threshold: -0.025,
    exit_threshold: 0.015,
    hold_time: 300,
    selectivity: 0.8,
    trade_size: 100,
    max_open_positions: 3
  },
  role: 'baby',
  current_status: 'testing'
});
```

### Record a Mutation

```javascript
await memory.recordMutation({
  mutation_id: 'mut_001',
  source_bot_id: 'bot_meanrev_001_gen1',
  resulting_bot_ids: [
    'bot_meanrev_001_gen2_canonical',
    'bot_meanrev_001_gen2_var1', // ... up to var10
  ],
  hypothesis_id: 'hyp_meanrev_001',
  diagnosis: 'high flip rate',
  mutation_type: 'selectivity',
  parameter_changes: {
    selectivity: { before: 0.8, after: 0.6 }
  },
  rationale: 'Reduce entry frequency to lower whipsaw trades',
  expected_effect: 'lower flip rate'
});
```

### Rocky's Reasoning Queries

```javascript
// 1. Why does this bot exist?
const origin = await memory.explainBotOrigin('bot_meanrev_001_gen1');
console.log(origin);
// {
//   bot_id: 'bot_meanrev_001_gen1',
//   hypothesis: { ... },
//   generation: 1,
//   creation_source: 'manual',
//   mutation_info: null,
//   created_at: '2026-04-18T...'
// }

// 2. What has been tried on this hypothesis?
const history = await memory.hypothesisMutationHistory('hyp_meanrev_001');
console.log(history);
// {
//   total_mutations: 5,
//   by_type: { selectivity: 2, exit: 2, entry: 1 },
//   by_result: {
//     helped: [...],
//     hurt: [...],
//     inconclusive: [...],
//     pending: [...]
//   }
// }

// 3. Is this problem new or repeated?
const priorAttempts = await memory.findPriorAttempts('high flip rate');
console.log(priorAttempts);
// [ {...}, {...} ] — all prior mutations with this diagnosis

// 4. Has this hypothesis ever worked?
const performance = await memory.hypothesisPerformanceSummary('hyp_meanrev_001');
console.log(performance);
// {
//   hypothesis_id: 'hyp_meanrev_001',
//   status: 'testing',
//   total_bots: 5,
//   strongest_bot_id: 'bot_meanrev_001_gen3_canonical',
//   generations: 3,
//   active_bots: 2,
//   best_performance: { trades: 45, flip_rate: 0.12, ... }
// }

// 5. Why promote/kill this bot?
const context = await memory.promotionDecisionContext('bot_meanrev_001_gen3_canonical');
console.log(context);
// {
//   bot_id: 'bot_meanrev_001_gen3_canonical',
//   current_metrics: { ... },
//   hypothesis_status: 'promising',
//   hypothesis_performance: { ... },
//   mutation_attempts_on_hypothesis: 5,
//   recent_decisions: [ ... ],
//   alignment: { ... }
// }
```

### Record Decisions

```javascript
await memory.recordDecision({
  decision_id: 'dec_001',
  related_bot_id: 'bot_meanrev_001_gen3_canonical',
  related_hypothesis_id: 'hyp_meanrev_001',
  source: 'user',
  decision_type: 'promote_bot',
  context_snapshot: {
    flip_rate: 0.12,
    shadow_pnl: 0.045,
    trades: 45,
    survival: 0.95
  },
  reason: 'Mutation to selectivity helped. Ready to test with real capital.'
});
```

## Event Hooks

THINK Memory should update on these events from Arena:

- `bot_spawned` → `createBot()`
- `mutation_applied` → `recordMutation()`
- `evaluation_complete` → `updateBotMetrics()` + `updateMutationResult()`
- `trajectory_updated` → `updateBotMetrics()`
- `approve_proposal` / `reject_proposal` → `recordDecision()`
- `promote_bot` / `kill_bot` / `switch` → `recordDecision()` + `updateBotMetrics()`
- `control_action` → `recordDecision()`

## Notes

- **Do NOT store every tick.** Update only at state changes.
- **Do NOT duplicate Arena truth.** THINK stores interpreted snapshots, not real-time metrics.
- **Do index heavily.** These queries are Rocky's lifeline.
- **Keep JSON columns queryable.** If performance becomes an issue, normalize them.

## Files

- `think-memory-schema.sql` — DDL and indexes
- `think-memory-queries.js` — Query layer (THINKMemory class)
- `init-think-memory.js` — Setup script

---

**Rocky's Memory. Your System's Reasoning Engine.**
