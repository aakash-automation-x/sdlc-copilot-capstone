import os, json, sys

try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

fp = d.get("file_path", "")
if not fp:
    sys.exit(0)

fp_norm = fp.replace("\\", "/")
if "data/" not in fp_norm or not fp.endswith(".json"):
    sys.exit(0)

if not os.path.exists(fp):
    sys.exit(0)

try:
    with open(fp, "r", encoding="utf-8") as f:
        json.load(f)
    print(f"JSON valid: {fp}")
except json.JSONDecodeError as e:
    print(f"INVALID JSON in {fp}: {e}", file=sys.stderr)
    sys.exit(1)
