import os, json, sys

try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

fp = d.get("file_path", "")
if not fp:
    sys.exit(0)

fp_norm = fp.replace("\\", "/")
if "/test/" in fp_norm or fp_norm.startswith("test/"):
    print(f"BLOCKED: Editing existing test files is not allowed per project rules ({fp}).")
    sys.exit(1)
