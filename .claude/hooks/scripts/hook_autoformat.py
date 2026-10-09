"""PostToolUse hook — auto-format Python files with ruff or black after every edit."""
import os, json, sys, shutil, subprocess

try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

fp = d.get("file_path", "")
if not fp or not fp.endswith(".py") or not os.path.exists(fp):
    sys.exit(0)

# Skip hook scripts themselves to avoid noisy self-formatting
fp_norm = fp.replace("\\", "/")
if ".claude/hooks/scripts/" in fp_norm:
    sys.exit(0)

if shutil.which("ruff"):
    print(f"[hook] Auto-formatting {os.path.basename(fp)} with ruff ...")
    subprocess.run(["ruff", "format", fp])
elif shutil.which("black"):
    print(f"[hook] Auto-formatting {os.path.basename(fp)} with black ...")
    subprocess.run(["black", fp, "--quiet"])
# Neither available — skip silently
