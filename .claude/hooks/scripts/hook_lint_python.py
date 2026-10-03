import os, json, sys, shutil, subprocess

try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

fp = d.get("file_path", "")
if not fp or not fp.endswith(".py"):
    sys.exit(0)

if not os.path.exists(fp):
    sys.exit(0)

if not shutil.which("ruff"):
    # ruff not installed — skip silently
    sys.exit(0)

print(f"[hook] Linting {os.path.basename(fp)} with ruff ...")
result = subprocess.run(
    ["ruff", "check", fp, "--select", "E,W,S", "--output-format", "concise"],
    capture_output=False,
)
sys.exit(result.returncode)
