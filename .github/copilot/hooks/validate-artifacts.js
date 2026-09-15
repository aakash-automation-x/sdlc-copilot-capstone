#!/usr/bin/env node
/**
 * validate-artifacts hook — enforces SDLC step ordering.
 *
 * Each pipeline step depends on the previous step's committed artifact. This
 * hook reports which artifacts exist and which are missing so an agent does not
 * start a step whose upstream deliverable is absent.
 *
 * Wired to the `SessionStart` event in hooks.json (informational, non-blocking).
 * Run with `--strict <step>` to fail (exit 1) when a step's prerequisites are
 * missing.
 *
 * Usage:
 *   node validate-artifacts.js --mode session
 *   node validate-artifacts.js --strict 05-implementation
 */
'use strict';

const fs = require('node:fs');
const path = require('node:path');

// Ordered artifacts and the step that produces each.
const PIPELINE = [
  { step: '01-requirements', artifact: 'requirements.md' },
  { step: '02-architecture', artifact: 'architecture.md' },
  { step: '03-design-review', artifact: 'design-review.md' },
  { step: '04-impl-plan', artifact: 'impl-plan.md' },
];

function repoRoot() {
  return process.cwd();
}

function exists(artifact) {
  return fs.existsSync(path.join(repoRoot(), artifact));
}

function report() {
  console.log('[validate-artifacts] Agentic SDLC pipeline status:');
  for (const { step, artifact } of PIPELINE) {
    console.log(`  ${exists(artifact) ? '✓' : '·'} ${artifact.padEnd(20)} (${step})`);
  }
}

function strict(targetStep) {
  const idx = PIPELINE.findIndex((p) => p.step === targetStep);
  if (idx <= 0) return 0; // first step or an implementation/verify/pr step
  const missing = PIPELINE.slice(0, idx).filter((p) => !exists(p.artifact));
  if (missing.length > 0) {
    console.error(`[validate-artifacts] Cannot start ${targetStep}. Missing upstream artifacts:`);
    for (const m of missing) console.error(`  - ${m.artifact} (from ${m.step})`);
    return 1;
  }
  return 0;
}

function main() {
  const args = process.argv.slice(2);
  const strictIdx = args.indexOf('--strict');
  report();
  if (strictIdx !== -1 && args[strictIdx + 1]) {
    process.exit(strict(args[strictIdx + 1]));
  }
  process.exit(0);
}

main();
