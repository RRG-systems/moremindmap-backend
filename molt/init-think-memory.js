#!/usr/bin/env node

// Initialize THINK Memory database
// Run once to create schema and indexes

const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

const MOLT_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'molt');
const DB_PATH = path.join(MOLT_DIR, 'think-memory.db');
const SCHEMA_PATH = path.join(MOLT_DIR, 'think-memory-schema.sql');

async function initDatabase() {
  return new Promise((resolve, reject) => {
    // Ensure molt directory exists
    if (!fs.existsSync(MOLT_DIR)) {
      fs.mkdirSync(MOLT_DIR, { recursive: true });
    }

    const db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        reject(err);
        return;
      }

      // Read and execute schema
      const schema = fs.readFileSync(SCHEMA_PATH, 'utf8');
      
      db.exec(schema, (err) => {
        if (err) {
          reject(err);
          return;
        }

        console.log('✓ THINK Memory database initialized');
        console.log(`  Database: ${DB_PATH}`);
        console.log('  Tables: hypotheses, bots, mutations, decisions');
        console.log('  Status: Ready for use');

        db.close();
        resolve();
      });
    });
  });
}

initDatabase()
  .then(() => {
    console.log('\nTHINK Memory is ready.');
    process.exit(0);
  })
  .catch((err) => {
    console.error('Error initializing THINK Memory:', err);
    process.exit(1);
  });
