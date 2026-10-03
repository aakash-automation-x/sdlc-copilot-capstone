import os, json, sys

try:
    d = json.loads(os.environ.get("CLAUDE_TOOL_INPUT", "{}"))
except json.JSONDecodeError:
    sys.exit(0)

fp = d.get("file_path", "")
if "models.py" in fp:
    print("REMINDER: models.py has TWO Vehicle classes (ORM + Pydantic). Verify the ORM Vehicle is not shadowed by this edit.")
