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

os.makedirs("logs", exist_ok=True)
with open("logs/commands.log", "a", encoding="utf-8") as f:
    f.write(line + "\n")
