import subprocess, sys

result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
added = [l for l in result.stdout.splitlines() if l.startswith("+") and not l.startswith("+++")]

keywords = ["password=", "secret=", "api_key=", "token=", "passwd=", "pwd="]
found = [l for l in added if any(k in l.lower() for k in keywords)]

if found:
    print("WARNING: Possible secrets detected in staged changes:")
    for line in found:
        print(f"  {line[:120]}")
    sys.exit(1)
