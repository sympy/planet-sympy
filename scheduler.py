#! /usr/bin/env python

import schedule
import time
import os

def job():
    print("Launching job (./update.sh)...")
    os.system("./update.sh")
    print("Job finished.")

schedule.every(10).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
