#! /usr/bin/env python

import os
import subprocess
import time

def job(silence_error=False):
    print("Launching job (./update.sh)...")
    result = subprocess.Popen("./update.sh")
    text = result.communicate()[0]
    returncode = result.returncode
    if not silence_error:
        if returncode != 0:
            raise Exception("Return code is non zero.")
    print("Job finished.")

print("Docker environment variables:")
if os.environ.get("SSH_PRIVATE_KEY"):
    deploy_token_display = "<non-emtpy ssh private key>"
else:
    deploy_token_display = "<empty>"
print("SSH_PRIVATE_KEY =", deploy_token_display)
print("TESTING =", os.environ.get("TESTING"))
print("Running job()")
job()
