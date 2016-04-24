#! /usr/bin/env python

import os
import subprocess
import time

import schedule

def job(silence_error=True):
    print("Launching job (./update.sh)...")
    result = subprocess.Popen("./update.sh")
    text = result.communicate()[0]
    returncode = result.returncode
    if not silence_error:
        if returncode != 0:
            raise Exception("Return code is non zero.")
    assert returncode
    print("Job finished.")

schedule.every(20).minutes.do(job)

print("Scheduler started...")
print("Docker environment variables:")
if os.environment.get("DEPLOY_TOKEN"):
    deploy_token_display = "<non-emtpy deploy token>"
else:
    deploy_token_display = "<empty>"
print("DEPLOY_TOKEN =", deploy_token_display)
print("TRAVIS =", os.environment.get("TRAVIS"))
if os.environ.get("TRAVIS") == "true":
    print("Running on Travis, calling job() 2x.")
    job(False)
    time.sleep(1)
    job(False)
else:
    while True:
        schedule.run_pending()
        time.sleep(1)
