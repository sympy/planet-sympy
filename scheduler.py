#!/usr/bin/env python3

import os
import subprocess
import time

def job(silence_error=False):
    print("Launching job (./update.sh)...")
    result = subprocess.run(["./update.sh"], capture_output=True, text=True)
    returncode = result.returncode
    if not silence_error and returncode != 0:
        raise Exception(f"Return code is non zero: {returncode}")
    print("Job finished.")

print("Docker environment variables:")
if os.environ.get("SSH_PRIVATE_KEY"):
    deploy_token_display = "<non-empty ssh private key>"
else:
    deploy_token_display = "<empty>"
print("SSH_PRIVATE_KEY =", deploy_token_display)
print("TESTING =", os.environ.get("TESTING"))
print("Running job()")
job()