#!/usr/bin/env node
/**
 * check-secrets hook — blocks credentials, tokens, and keys from being committed.
 *
 * Wired to the `PreToolUse` (shell/git) and `Stop` events in hooks.json.
 * Exit code 0 = allow; non-zero = block the action and report the finding.
 *
 * Usage:
 *   node check-secrets.js            # scan working-tree changes vs HEAD
 *   node check-secrets.js --staged   # scan staged changes only
 */
'use strict';

const { execSync } = require('node:child_process');

const SECRET_PATTERNS = [
  { name: 'AWS access key id', re: /AKIA[0-9A-Z]{16}/ },
  { name: 'Private key block', re: /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/ },
  { name: 'GitHub token', re: /gh[pousr]_[0-9A-Za-z]{36,}/ },
  { name: 'Slack token', re: /xox[baprs]-[0-9A-Za-z-]{10,}/ },
  { name: 'Generic API/secret assignment', re: /(?:api[_-]?key|secret|token|password|passwd|pwd)\s*[:=]\s*['"][^'"]{8,}['"]/i },
  { name: 'Jira/Confluence personal token env', re: /(?:JIRA_PERSONAL_TOKEN|CONFLUENCE_API_TOKEN)\s*[:=]\s*['"][^'"]+['"]/ },
];

// Paths that are allowed to contain example/placeholder secret-like strings.
const IGNORED = [/(^|\/)\.env\.example$/, /(^|\/)hooks\/check-secrets\.js$/];

function getDiff(staged) {
  try {
    const args = staged ? '--cached' : '';
    return execSync(`git diff ${args} --unified=0`, { encoding: 'utf8' });
  } catch {
    return '';
  }
}

function scan(diff) {
  const findings = [];
  let currentFile = null;
  for (const line of diff.split('\n')) {
    const fileMatch = line.match(/^\+\+\+ b\/(.+)$/);
    if (fileMatch) {
      currentFile = fileMatch[1];
      continue;
    }
    if (!line.startsWith('+') || line.startsWith('+++')) continue;
    if (currentFile && IGNORED.some((re) => re.test(currentFile))) continue;
    for (const { name, re } of SECRET_PATTERNS) {
      if (re.test(line)) {
        findings.push({ file: currentFile || '(unknown)', kind: name });
      }
    }
  }
  return findings;
}

function main() {
  const staged = process.argv.includes('--staged');
  const findings = scan(getDiff(staged));
  if (findings.length === 0) {
    process.exit(0);
  }
  console.error('\n[check-secrets] Potential secrets detected — action blocked:');
  for (const f of findings) {
    console.error(`  - ${f.kind} in ${f.file}`);
  }
  console.error('\nRemove the secret, use an environment variable or secrets manager, then retry.');
  process.exit(1);
}

main();
