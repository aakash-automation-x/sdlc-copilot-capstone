import subprocess
import sys

print("[hook] Session ended — running test summary ...")
subprocess.run([sys.executable, "-m", "pytest", "test/test_vehicle.py", "-q", "--tb=line"])
