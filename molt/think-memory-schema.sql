-- THINK Memory Schema
-- SQLite relational layer for bot, hypothesis, mutation, and decision history
-- Arena remains truth source for execution metrics
-- THINK stores compressed, queryable history at state changes only

-- =====================================================
-- HYPOTHESES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS hypotheses (
  hypothesis_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  target_market TEXT,
  target_regime TEXT,
    -- ranging | trending | high_vol | low_vol | mixed
  expected_behavior TEXT,
  failure_modes TEXT,
    -- JSON array of failure mode strings
  allowed_parameter_clusters TEXT,
    -- JSON array: entry, exit, hold, selectivity, size, concentration
  status TEXT DEFAULT 'testing',
    -- testing | promising | weak | broken | retired
  supporting_bots TEXT,
    -- JSON array of bot_ids currently testing this hypothesis
  strongest_bot_id TEXT,
    -- bot_id with best performance on this hypothesis
  notes_summary TEXT,
    -- human-readable summary of hypothesis behavior so far
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- BOTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS bots (
  bot_id TEXT PRIMARY KEY,
  parent_bot_id TEXT,
  generation INTEGER DEFAULT 1,
  hypothesis_id TEXT NOT NULL,
  creation_source TEXT NOT NULL,
    -- manual | rocky_proposal | seed_agent | molt_feed
  created_by_mutation_id TEXT,
    -- NULL if manual creation, else mutation_id that spawned this bot
  
  -- DNA Snapshot (current expression)
  dna_json TEXT NOT NULL,
    -- JSON: entry_threshold, exit_threshold, hold_time, selectivity, trade_size, max_open_positions
  
  role TEXT DEFAULT 'baby',
    -- active | baby | control | retired
  current_status TEXT DEFAULT 'testing',
    -- testing | active | paused | failed | promoted | retired
  current_run_id TEXT,
    -- which arena run is this bot in
  
  -- Latest Metrics Snapshot (updated at evaluation, promotion, mutation result)
  latest_metrics_json TEXT,
    -- JSON: trades, flip_rate, shadow_pnl, divergence, drawdown, survival, trajectory, control_action
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  retired_at DATETIME,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(hypothesis_id),
  FOREIGN KEY (created_by_mutation_id) REFERENCES mutations(mutation_id)
);

-- =====================================================
-- MUTATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS mutations (
  mutation_id TEXT PRIMARY KEY,
  source_bot_id TEXT NOT NULL,
  resulting_bot_ids TEXT NOT NULL,
    -- JSON array of 11 bot_ids (0 canonical + 1-10 variants)
  hypothesis_id TEXT NOT NULL,
  source_proposal_id TEXT,
    -- if from rocky proposal, link to it
  
  diagnosis TEXT NOT NULL,
    -- what problem was identified (e.g., "high flip rate")
  mutation_type TEXT NOT NULL,
    -- exit | selectivity | size | entry | hold | concentration
  parameter_changes TEXT NOT NULL,
    -- JSON: {param_name: {before: X, after: Y}, ...}
  rationale TEXT NOT NULL,
    -- why this mutation was chosen
  expected_effect TEXT,
    -- lower flip rate, lower drawdown, etc.
  
  result TEXT DEFAULT 'pending',
    -- helped | hurt | inconclusive | pending
  result_summary TEXT,
    -- brief explanation of result
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  evaluated_at DATETIME,
  
  FOREIGN KEY (source_bot_id) REFERENCES bots(bot_id),
  FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(hypothesis_id)
);

-- =====================================================
-- DECISIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS decisions (
  decision_id TEXT PRIMARY KEY,
  related_bot_id TEXT,
  related_hypothesis_id TEXT,
  related_mutation_id TEXT,
  
  source TEXT NOT NULL,
    -- user | rocky | control_layer
  decision_type TEXT NOT NULL,
    -- approve_proposal | reject_proposal | promote_bot | kill_bot | 
    -- start_new_run | hold | switch | control_action
  
  context_snapshot TEXT,
    -- JSON of key metrics at decision time
  reason TEXT NOT NULL,
    -- why this decision was made
  
  outcome TEXT,
    -- null initially; later updated with result summary
  
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (related_bot_id) REFERENCES bots(bot_id),
  FOREIGN KEY (related_hypothesis_id) REFERENCES hypotheses(hypothesis_id),
  FOREIGN KEY (related_mutation_id) REFERENCES mutations(mutation_id)
);

-- =====================================================
-- INDICES FOR COMMON QUERIES
-- =====================================================

-- Query 1: Why does this bot exist?
CREATE INDEX IF NOT EXISTS idx_bots_hypothesis ON bots(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_bots_parent ON bots(parent_bot_id);
CREATE INDEX IF NOT EXISTS idx_bots_mutation ON bots(created_by_mutation_id);

-- Query 2: What has been tried on this hypothesis?
CREATE INDEX IF NOT EXISTS idx_mutations_hypothesis ON mutations(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_mutations_result ON mutations(result);

-- Query 3: Is this problem repeated?
CREATE INDEX IF NOT EXISTS idx_mutations_diagnosis ON mutations(diagnosis);

-- Query 4: Has this hypothesis ever worked?
CREATE INDEX IF NOT EXISTS idx_hypotheses_status ON hypotheses(status);
CREATE INDEX IF NOT EXISTS idx_bots_status ON bots(current_status);

-- Query 5: Why promote/kill?
CREATE INDEX IF NOT EXISTS idx_decisions_type ON decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_decisions_bot ON decisions(related_bot_id);

-- =====================================================
-- MOLT FEED TABLE (Phase 3.1)
-- =====================================================
-- Append-only log of seed agent posts, proposals, disagreements
-- Traceable lineage: agent post → hypothesis → spawned bots

CREATE TABLE IF NOT EXISTS molt_feed (
  molt_id TEXT PRIMARY KEY,
  agent_name TEXT NOT NULL,
    -- 'Overfitter' | 'Explorer' | 'Risk Manager'
  post_type TEXT NOT NULL,
    -- 'note' | 'proposal' | 'disagreement'
  
  -- Content
  content_text TEXT NOT NULL,
    -- raw post content
  topic TEXT,
    -- 'performance', 'exploration', 'risk', etc.
  
  -- For proposals: link to hypothesis
  linked_hypothesis_id TEXT,
    -- reference to hypothesis created by this proposal
  linked_bot_ids TEXT,
    -- JSON array of bot_ids spawned from this proposal
  
  -- For disagreements: link to prior post
  replies_to_molt_id TEXT,
  replies_to_agent_name TEXT,
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (linked_hypothesis_id) REFERENCES hypotheses(hypothesis_id)
);

-- =====================================================
-- MOLT SPAWNS TABLE (Phase 3.1)
-- =====================================================
-- Explicit lineage: agent proposal → hypothesis → 11 bot IDs

CREATE TABLE IF NOT EXISTS molt_spawns (
  spawn_id TEXT PRIMARY KEY,
  molt_id TEXT NOT NULL,
    -- which agent post triggered this spawn
  hypothesis_id TEXT NOT NULL,
    -- created hypothesis
  canonical_bot_id TEXT NOT NULL,
    -- the 1 canonical variant
  variant_bot_ids TEXT NOT NULL,
    -- JSON array of 10 variant bot_ids
  
  spawn_reason TEXT,
    -- 'aggressive_scaling', 'volatility_mr', 'defensive_positioning', etc.
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (molt_id) REFERENCES molt_feed(molt_id),
  FOREIGN KEY (hypothesis_id) REFERENCES hypotheses(hypothesis_id),
  FOREIGN KEY (canonical_bot_id) REFERENCES bots(bot_id)
);

-- =====================================================
-- MOLT INDICES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_molt_feed_agent ON molt_feed(agent_name);
CREATE INDEX IF NOT EXISTS idx_molt_feed_type ON molt_feed(post_type);
CREATE INDEX IF NOT EXISTS idx_molt_feed_hypothesis ON molt_feed(linked_hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_molt_spawns_hypothesis ON molt_spawns(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_molt_spawns_molt ON molt_spawns(molt_id);
