"""PostToolUse hook for Edit/Write — runs all post-edit checks in one script."""
import os, json, sys, shutil, subprocess

try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

fp = d.get("file_path", "")
if not fp:
    sys.exit(0)

fp_norm = fp.replace("\\", "/")
basename = os.path.basename(fp)

# --- Check 1: validate JSON files under data/ ---
if "data/" in fp_norm and fp.endswith(".json") and os.path.exists(fp):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            json.load(f)
        print(f"[hook] JSON valid: {fp}")
    except json.JSONDecodeError as e:
        print(f"[hook] INVALID JSON in {fp}: {e}", file=sys.stderr)
        sys.exit(1)

# --- Check 2: lint with ruff if available (only app/ Python files) ---
if fp.endswith(".py") and "app/" in fp_norm and os.path.exists(fp):
    if shutil.which("ruff"):
        print(f"[hook] Linting {basename} with ruff ...")
        result = subprocess.run(["ruff", "check", fp, "--select", "E,W,S", "--output-format", "concise"])
        if result.returncode != 0:
            print(f"[hook] Lint issues found in {basename} (non-blocking) — fix before committing.")

# --- Check 4: run gated tests after any app/ Python edit ---
if fp.endswith(".py") and "app/" in fp_norm and os.path.exists(fp):
    print(f"[hook] Running gated tests after edit to {basename} ...")
    result = subprocess.run(
        ["pytest", "test/test_vehicle.py", "-q", "--tb=short"],
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"[hook] Tests FAILED after edit to {basename} — review output above.")
        sys.exit(1)
    sys.exit(0)
