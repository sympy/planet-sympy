#! /usr/bin/env python

import schedule
import time
import os

def job():
    print("Launching job (./update.sh)...")
    os.system("./update.sh")
    print("Job finished.")

schedule.every(20).minutes.do(job)

print("Scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(1)
