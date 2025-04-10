#!/usr/bin/env python3

import sys
import readline
from cli.logiclance_terminal import terminal_shell
import json
import getpass
import os
import subprocess
import hashlib
from utils.config_loader import load_setup_config


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


def source_tool_configs():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "configs", "setup_config.json")
        with open(config_path) as f:
            config = json.load(f)
            tool_configs = config.get("tool_config", [])
            for tool in tool_configs:
                sh_path = tool.get("launch_sh_path")
                if sh_path and os.path.exists(sh_path):
                    print(f"🔧 Sourcing tool config: {sh_path}")
                    subprocess.call(f"source {sh_path}", shell=True, executable="/bin/bash")
                else:
                    print(f"⚠️  Skipping missing tool config: {sh_path}")
    except Exception as e:
        print(f"❌ Error sourcing configs: {e}")

    
def show_usage():
    org_name = "N/A"
    developer = "Hemanth Kumar DM"
    contact = "dmhemanthkumar7@gmail.com"

    try:
        config = load_setup_config()
        org_name = config.get("org_name", org_name)
    except Exception:
        pass  # Do not reference config here again!


    print(f"""
Logic Lance — ASIC Flow Automation Tool
-------------------------------------------
Version       : v1.0.0
Developer     : {developer}
Organization  : {org_name}
Contact       : {contact}

Usage:
    logiclance <username>     Start interactive shell for a user

Description:
    Logic Lance is a role-based ASIC flow automation platform.
    Users can interactively run only the flows permitted to them,
    and access relevant project RTL, LIB, LEF, and SDC files.

Type a logiclance <user_name> to get started!
""")

def find_user(config, username):
    for user in config.get("employees", []):
        if user["name"].lower() == username:
            return user
    return None

import readline
import os


def main():
    show_logiclance_banner()
    if len(sys.argv) == 1:
        show_usage()
        return

    username = sys.argv[1].strip().lower()
    setup_config = load_setup_config()

    user = find_user(setup_config, username)
    if not user:
        print(f"❌ User '{username}' not found in setup_config.json.")
        return

    password = getpass.getpass("🔐 Enter password: ").strip()
    if password != user["password"]:
        print("❌ Incorrect password.")
        return

    # ✅ Only source tool configs once
    source_tool_configs()

    # ✅ Only enter shell once
    terminal_shell(user)


if __name__ == "__main__":
    main()
