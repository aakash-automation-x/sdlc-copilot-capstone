import subprocess

print("[hook] Session ended — running test summary ...")
subprocess.run(["pytest", "test/test_vehicle.py", "-q", "--tb=line"])
