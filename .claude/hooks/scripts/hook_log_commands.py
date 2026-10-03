"""PostToolUse hook — append every executed Bash command to logs/commands.log."""
import os, json, sys
from datetime import datetime, timezone

try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

command = d.get("command", "").strip()
if not command:
    sys.exit(0)

description = d.get("description", "")
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

line = f"[{timestamp}] {command}"
if description:
    line += f"  # {description}"

# Anchor log path to project root via __file__
# __file__ = .claude/hooks/scripts/hook_log_commands.py  →  ../../.. = project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
log_dir = os.path.join(ROOT, "logs")
os.makedirs(log_dir, exist_ok=True)
with open(os.path.join(log_dir, "commands.log"), "a", encoding="utf-8") as f:
    f.write(line + "\n")
