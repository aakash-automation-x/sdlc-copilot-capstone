import os, json, sys, subprocess

try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

fp = d.get("file_path", "")
if not fp or not fp.endswith(".py"):
    sys.exit(0)

# Skip if the edit is inside the test directory itself (guard hook handles that)
fp_norm = fp.replace("\\", "/")
if "/test/" in fp_norm or fp_norm.startswith("test/"):
    sys.exit(0)

print(f"[hook] Running gated tests after edit to {os.path.basename(fp)} ...")
result = subprocess.run(
    ["pytest", "test/test_vehicle.py", "-v", "--tb=short", "-q"],
    capture_output=False,
)
sys.exit(result.returncode)
