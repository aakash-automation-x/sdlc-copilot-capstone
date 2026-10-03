"""PreToolUse hook — block git commits that contain credential keywords in staged diff."""
import os, json, subprocess, sys

# In-script guard: belt-and-suspenders check alongside the Bash(git commit*) matcher
try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

cmd = d.get("command", "").strip()
if not cmd.startswith("git commit"):
    sys.exit(0)

result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
if result.returncode != 0:
    sys.exit(0)

added = [l for l in result.stdout.splitlines() if l.startswith("+") and not l.startswith("+++")]

keywords = ["password=", "secret=", "api_key=", "token=", "passwd=", "pwd="]
found = [l for l in added if any(k in l.lower() for k in keywords)]

if found:
    print("WARNING: Possible secrets detected in staged changes:")
    for line in found:
        print(f"  {line[:120]}")
    sys.exit(1)
