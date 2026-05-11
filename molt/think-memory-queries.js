// THINK Memory Query Layer
// Provides Rocky with queryable reasoning about bots, hypotheses, mutations, decisions

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const THINK_DB_PATH = path.join(process.env.HOME, '.openclaw', 'workspace', 'molt', 'think-memory.db');

class THINKMemory {
  constructor() {
    this.db = null;
  }

  init() {
    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database(THINK_DB_PATH, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ id: this.lastID, changes: this.changes });
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows || []);
      });
    });
  }

  // =====================================================
  // HYPOTHESIS OPERATIONS
  // =====================================================

  async createHypothesis(hypothesis) {
    const {
      hypothesis_id,
      title,
      description,
      target_market,
      target_regime,
      expected_behavior,
      failure_modes,
      allowed_parameter_clusters,
      notes_summary
    } = hypothesis;

    const sql = `
      INSERT INTO hypotheses 
      (hypothesis_id, title, description, target_market, target_regime, 
       expected_behavior, failure_modes, allowed_parameter_clusters, 
       supporting_bots, notes_summary, status)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'testing')
    `;

    return this.run(sql, [
      hypothesis_id,
      title,
      description,
      target_market,
      target_regime,
      expected_behavior,
      JSON.stringify(failure_modes || []),
      JSON.stringify(allowed_parameter_clusters || []),
      JSON.stringify([]), // supporting_bots starts empty
      notes_summary
    ]);
  }

  async getHypothesis(hypothesis_id) {
    const sql = `SELECT * FROM hypotheses WHERE hypothesis_id = ?`;
    const row = await this.get(sql, [hypothesis_id]);
    if (row) {
      row.failure_modes = JSON.parse(row.failure_modes || '[]');
      row.allowed_parameter_clusters = JSON.parse(row.allowed_parameter_clusters || '[]');
      row.supporting_bots = JSON.parse(row.supporting_bots || '[]');
    }
    return row;
  }

  async updateHypothesisStatus(hypothesis_id, status, notes_summary) {
    const sql = `
      UPDATE hypotheses 
      SET status = ?, notes_summary = ?, updated_at = CURRENT_TIMESTAMP
      WHERE hypothesis_id = ?
    `;
    return this.run(sql, [status, notes_summary, hypothesis_id]);
  }

  // =====================================================
  // BOT OPERATIONS
  // =====================================================

  async createBot(bot) {
    const {
      bot_id,
      parent_bot_id,
      generation,
      hypothesis_id,
      creation_source,
      created_by_mutation_id,
      dna_json,
      role,
      current_status,
      current_run_id,
      latest_metrics_json
    } = bot;

    const sql = `
      INSERT INTO bots 
      (bot_id, parent_bot_id, generation, hypothesis_id, creation_source,
       created_by_mutation_id, dna_json, role, current_status, current_run_id,
       latest_metrics_json)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    return this.run(sql, [
      bot_id,
      parent_bot_id || null,
      generation || 1,
      hypothesis_id,
      creation_source,
      created_by_mutation_id || null,
      typeof dna_json === 'string' ? dna_json : JSON.stringify(dna_json),
      role || 'baby',
      current_status || 'testing',
      current_run_id || null,
      typeof latest_metrics_json === 'string' ? latest_metrics_json : JSON.stringify(latest_metrics_json || {})
    ]);
  }

  async getBot(bot_id) {
    const sql = `SELECT * FROM bots WHERE bot_id = ?`;
    const row = await this.get(sql, [bot_id]);
    if (row) {
      row.dna_json = JSON.parse(row.dna_json);
      row.latest_metrics_json = JSON.parse(row.latest_metrics_json || '{}');
    }
    return row;
  }

  async getBotsByHypothesis(hypothesis_id) {
    const sql = `SELECT * FROM bots WHERE hypothesis_id = ? ORDER BY created_at DESC`;
    const rows = await this.all(sql, [hypothesis_id]);
    return rows.map(row => {
      row.dna_json = JSON.parse(row.dna_json);
      row.latest_metrics_json = JSON.parse(row.latest_metrics_json || '{}');
      return row;
    });
  }

  async updateBotMetrics(bot_id, metrics_json) {
    const sql = `
      UPDATE bots 
      SET latest_metrics_json = ?, current_status = ?, updated_at = CURRENT_TIMESTAMP
      WHERE bot_id = ?
    `;
    return this.run(sql, [
      typeof metrics_json === 'string' ? metrics_json : JSON.stringify(metrics_json),
      'active',
      bot_id
    ]);
  }

  async retireBot(bot_id) {
    const sql = `
      UPDATE bots 
      SET current_status = 'retired', retired_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
      WHERE bot_id = ?
    `;
    return this.run(sql, [bot_id]);
  }

  // =====================================================
  // MUTATION OPERATIONS
  // =====================================================

  async recordMutation(mutation) {
    const {
      mutation_id,
      source_bot_id,
      resulting_bot_ids,
      hypothesis_id,
      source_proposal_id,
      diagnosis,
      mutation_type,
      parameter_changes,
      rationale,
      expected_effect
    } = mutation;

    const sql = `
      INSERT INTO mutations 
      (mutation_id, source_bot_id, resulting_bot_ids, hypothesis_id,
       source_proposal_id, diagnosis, mutation_type, parameter_changes,
       rationale, expected_effect, result)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    `;

    return this.run(sql, [
      mutation_id,
      source_bot_id,
      typeof resulting_bot_ids === 'string' ? resulting_bot_ids : JSON.stringify(resulting_bot_ids),
      hypothesis_id,
      source_proposal_id || null,
      diagnosis,
      mutation_type,
      typeof parameter_changes === 'string' ? parameter_changes : JSON.stringify(parameter_changes),
      rationale,
      expected_effect || null
    ]);
  }

  async getMutationsByHypothesis(hypothesis_id) {
    const sql = `
      SELECT * FROM mutations 
      WHERE hypothesis_id = ? 
      ORDER BY created_at DESC
    `;
    const rows = await this.all(sql, [hypothesis_id]);
    return rows.map(row => {
      row.resulting_bot_ids = JSON.parse(row.resulting_bot_ids);
      row.parameter_changes = JSON.parse(row.parameter_changes);
      return row;
    });
  }

  async getMutationsByDiagnosis(diagnosis) {
    const sql = `
      SELECT * FROM mutations 
      WHERE diagnosis LIKE ? 
      ORDER BY created_at DESC
    `;
    const rows = await this.all(sql, [`%${diagnosis}%`]);
    return rows.map(row => {
      row.resulting_bot_ids = JSON.parse(row.resulting_bot_ids);
      row.parameter_changes = JSON.parse(row.parameter_changes);
      return row;
    });
  }

  async updateMutationResult(mutation_id, result, result_summary) {
    const sql = `
      UPDATE mutations 
      SET result = ?, result_summary = ?, evaluated_at = CURRENT_TIMESTAMP
      WHERE mutation_id = ?
    `;
    return this.run(sql, [result, result_summary, mutation_id]);
  }

  // =====================================================
  // DECISION OPERATIONS
  // =====================================================

  async recordDecision(decision) {
    const {
      decision_id,
      related_bot_id,
      related_hypothesis_id,
      related_mutation_id,
      source,
      decision_type,
      context_snapshot,
      reason
    } = decision;

    const sql = `
      INSERT INTO decisions 
      (decision_id, related_bot_id, related_hypothesis_id, related_mutation_id,
       source, decision_type, context_snapshot, reason)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `;

    return this.run(sql, [
      decision_id,
      related_bot_id || null,
      related_hypothesis_id || null,
      related_mutation_id || null,
      source,
      decision_type,
      typeof context_snapshot === 'string' ? context_snapshot : JSON.stringify(context_snapshot || {}),
      reason
    ]);
  }

  async getDecisionsByBot(bot_id) {
    const sql = `
      SELECT * FROM decisions 
      WHERE related_bot_id = ? 
      ORDER BY timestamp DESC
    `;
    const rows = await this.all(sql, [bot_id]);
    return rows.map(row => {
      row.context_snapshot = JSON.parse(row.context_snapshot || '{}');
      return row;
    });
  }

  // =====================================================
  // ROCKY'S REASONING QUERIES
  // =====================================================

  // Query 1: Why does this bot exist?
  async explainBotOrigin(bot_id) {
    const bot = await this.getBot(bot_id);
    if (!bot) return null;

    const hypothesis = await this.getHypothesis(bot.hypothesis_id);
    let mutationInfo = null;

    if (bot.created_by_mutation_id) {
      mutationInfo = await this.get(
        `SELECT * FROM mutations WHERE mutation_id = ?`,
        [bot.created_by_mutation_id]
      );
      if (mutationInfo) {
        mutationInfo.parameter_changes = JSON.parse(mutationInfo.parameter_changes);
      }
    }

    return {
      bot_id: bot.bot_id,
      hypothesis: hypothesis,
      generation: bot.generation,
      creation_source: bot.creation_source,
      parent_bot_id: bot.parent_bot_id,
      mutation_info: mutationInfo,
      created_at: bot.created_at
    };
  }

  // Query 2: What has been tried on this hypothesis?
  async hypothesisMutationHistory(hypothesis_id) {
    const mutations = await this.getMutationsByHypothesis(hypothesis_id);
    
    const summary = {
      total_mutations: mutations.length,
      by_type: {},
      by_result: {
        helped: [],
        hurt: [],
        inconclusive: [],
        pending: []
      }
    };

    mutations.forEach(mut => {
      summary.by_type[mut.mutation_type] = (summary.by_type[mut.mutation_type] || 0) + 1;
      if (summary.by_result[mut.result]) {
        summary.by_result[mut.result].push({
          mutation_id: mut.mutation_id,
          diagnosis: mut.diagnosis,
          parameter_changes: mut.parameter_changes,
          result_summary: mut.result_summary
        });
      }
    });

    return summary;
  }

  // Query 3: Is this problem new or repeated?
  async findPriorAttempts(diagnosis) {
    return this.getMutationsByDiagnosis(diagnosis);
  }

  // Query 4: Has this hypothesis ever worked?
  async hypothesisPerformanceSummary(hypothesis_id) {
    const hypothesis = await this.getHypothesis(hypothesis_id);
    const bots = await this.getBotsByHypothesis(hypothesis_id);

    const summary = {
      hypothesis_id,
      status: hypothesis.status,
      total_bots: bots.length,
      strongest_bot_id: hypothesis.strongest_bot_id,
      generations: Math.max(...bots.map(b => b.generation || 1), 0),
      active_bots: bots.filter(b => b.current_status === 'active').length,
      best_performance: null
    };

    if (hypothesis.strongest_bot_id) {
      const strongestBot = await this.getBot(hypothesis.strongest_bot_id);
      summary.best_performance = strongestBot?.latest_metrics_json;
    }

    return summary;
  }

  // Query 5: Why promote/kill?
  async promotionDecisionContext(bot_id) {
    const bot = await this.getBot(bot_id);
    const hypothesis = await this.getHypothesis(bot.hypothesis_id);
    const mutations = await this.getMutationsByHypothesis(bot.hypothesis_id);
    const decisions = await this.getDecisionsByBot(bot_id);

    return {
      bot_id,
      current_metrics: bot.latest_metrics_json,
      hypothesis_status: hypothesis.status,
      hypothesis_performance: await this.hypothesisPerformanceSummary(bot.hypothesis_id),
      mutation_attempts_on_hypothesis: mutations.length,
      recent_decisions: decisions.slice(0, 5),
      alignment: {
        matches_regime: true, // TODO: actual regime detection
        mutation_helped_recently: mutations.some(m => m.result === 'helped' && new Date(m.evaluated_at) > new Date(Date.now() - 24*60*60*1000))
      }
    };
  }

  close() {
    return new Promise((resolve, reject) => {
      if (this.db) {
        this.db.close((err) => {
          if (err) reject(err);
          else resolve();
        });
      } else {
        resolve();
      }
    });
  }
}

module.exports = THINKMemory;
