#!/usr/bin/env python3

import sys
import readline
import json
import getpass
import os
import subprocess
import hashlib
import csv
from cli.logiclance_terminal import terminal_shell


def show_logiclance_banner():
    banner = r"""
 /----------------------------------------------------------------------------\
 |                                                                            |
 |  logiclance -- ASIC Flow Automation Platform                               |
 |                                                                            |
 |  Copyright (C) 2024 - 2025  Hemanth Kumar DM <dmhemanthkumar7@gmail.com>   |
 |                                                                            |
 |  Permission is hereby granted, free of charge, to any person obtaining a   |
 |  copy of this software and associated documentation files (the "Software"),|
 |  to deal in the Software without restriction, including without limitation |
 |  the rights to use, copy, modify, merge, publish, distribute, sublicense,  |
 |  and/or sell copies of the Software, and to permit persons to whom the     |
 |  Software is furnished to do so, subject to the following conditions:      |
 |                                                                            |
 |  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR|
 |  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  |
 |  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL   |
 |  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER|
 |  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING   |
 |  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER       |
 |  DEALINGS IN THE SOFTWARE.                                                 |
 |                                                                            |
 \----------------------------------------------------------------------------/

 Logic Lance v1.0.0 — Developed by Hemanth Kumar DM
"""
    print(banner)


def show_usage():
    print("""
Logic Lance — ASIC Flow Automation Tool
-------------------------------------------
Usage:
    logiclance <project_name> <username>    Start interactive shell for a user

Description:
    Logic Lance is a role-based ASIC flow automation platform.
    Users can interactively run only the flows permitted to them,
    and access relevant project RTL, LIB, LEF, and SDC files.
""")

def verify_project_exists(project_name):
    root = os.environ.get("LOGICLANCE_ROOT")
    if not root:
        print("❌ LOGICLANCE_ROOT environment variable is not set.")
        return False

    project_path = os.path.join(root, "projects", project_name)
    print(f"🔍 Checking: {project_path}")
    return os.path.isdir(project_path)




def find_user_in_csv(project_name, username):
    config_root = os.environ.get("CONFIG_ROOT")
    if not config_root:
        print("❌ CONFIG_ROOT environment variable is not set.")
        return None

    csv_path = os.path.join(config_root, "employees.csv")
    if not os.path.isfile(csv_path):
        print(f"❌ employees.csv not found at {csv_path}")
        return None

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["name"].strip().lower() == username:
                return row
    return None


def verify_password(input_password, hashed_password):
    return hashlib.sha256(input_password.encode()).hexdigest() == hashed_password


def main():
    show_logiclance_banner()
    

    if len(sys.argv) != 3:
        show_usage()
        return

    project_name = sys.argv[1].strip()
    username = sys.argv[2].strip().lower()


    # ✅ Check project exists
    print("🔎 CONFIG_ROOT from environment:", os.environ.get("CONFIG_ROOT"))
    if not verify_project_exists(project_name):
        print(f"❌ Project '{project_name}' not found")
        return

    # ✅ Find user in project-specific CSV
    user = find_user_in_csv(project_name, username)
    if not user:
        print(f"❌ User '{username}' not found in employees.csv")
        return

    # 🔐 Prompt for password
    password = getpass.getpass("🔐 Enter password: ").strip()
    if not verify_password(password, user["password"]):
        print("❌ Incorrect password.")
        return

    print(f"✅ Welcome, {user['name']}!")
    

    # 🖥️ Launch Logic Lance interactive shell
    terminal_shell(user, project_name)


if __name__ == "__main__":
    main()
