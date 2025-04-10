# logiclance_terminal.py

import os
import readline
import json
from utils.config_loader import load_setup_config
from utils.config_loader import load_flow_config

import subprocess

HISTORY_FILE = os.path.expanduser("~/.logiclance_history")

# List of allowed flow commands
FLOW_COMMANDS = ["linting", "synthesis", "lec", "pnr"]
BUILTIN_COMMANDS = ["help", "exit", "quit", "history"]

def setup_readline(commands):
    def completer(text, state):
        options = [cmd for cmd in commands if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)

    try:
        readline.read_history_file(HISTORY_FILE)
    except FileNotFoundError:
        pass

def save_history():
    try:
        readline.write_history_file(HISTORY_FILE)
    except Exception:
        pass

def handle_builtin_command(cmd):
    if cmd == "help":
        print("Available commands: " + ", ".join(FLOW_COMMANDS + BUILTIN_COMMANDS))
    elif cmd == "history":
        try:
            with open(HISTORY_FILE, "r") as f:
                for i, line in enumerate(f, start=1):
                    print(f"{i:3}: {line.strip()}")
        except Exception:
            print("⚠️  No history available.")

def handle_flow_command(cmd, user):
    if user.get(cmd, "no").lower() != "yes":
        print(f"🚫 You are not allowed to run '{cmd}' flow.")
        return

    try:
        flow_config = load_flow_config()
        setup_config = load_setup_config()

        # Check for alias
        if cmd not in flow_config:
            aliases = flow_config.get("aliases", {})
            if cmd in aliases:
                stages = aliases[cmd]
                print(f"🔗 '{cmd}' is an alias for: {', '.join(stages)}")
                for stage in stages:
                    handle_flow_command(stage, user)
                return
            else:
                print(f"❌ Flow '{cmd}' not defined in flow_config.json.")
                return

        # Real flow
        flow = flow_config[cmd]
        tool_info = flow.get("tool_config", {})
        default_script = flow.get("script", "")
        tool_name = tool_info.get("tool", "UnknownTool")

        # Find launch script for the tool
        launch_path = None
        for tool in setup_config.get("tool_config", []):
            if tool.get("tool") == tool_name:
                launch_path = tool.get("launch_sh_path")
                break

        if not launch_path or not os.path.exists(launch_path):
            print(f"⚠️ Launch script for '{tool_name}' not found.")
            return

        # Prefer user script
        user_script = os.path.join("user_scripts", f"{cmd}.tcl")
        script_to_use = user_script if os.path.exists(user_script) else default_script

        if not os.path.exists(script_to_use):
            print(f"❌ Script not found: {script_to_use}")
            return

        print(f"🛠 Running '{cmd}' using {tool_name}...")
        subprocess.run(f"source {launch_path} && {tool_name} -file {script_to_use}",
                       shell=True, executable="/bin/bash")

    except Exception as e:
        print(f"❌ Error during flow execution: {e}")


def terminal_shell(user):
    config_path = os.path.join(os.path.dirname(__file__), "../configs/setup_config.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        config = {}

    print(f"\n🔓 Welcome to Logic Lance Shell, {user['name'].capitalize()}!")
    print(f" Project      : {config.get('project_name', 'N/A')}")
    print(f" Tech Node    : {config.get('tech_node', 'N/A')}")
    print(f" RTL Path     : {config.get('rtl_dir', 'N/A')}")
    print(f" LIB Path     : {config.get('lib_dir', 'N/A')}")
    print(f" LEF Path     : {config.get('lef_dir', 'N/A')}")
    print(f" SDC Path     : {config.get('sdc_dir', 'N/A')}")
    print(f" EDA Tool     : {config.get('eda_tool', 'N/A')} (v1.0)")
    print(f" Developer    : Hemanth Kumar DM <dmhemanthkumar7@gmail.com>")

    print("\nAllowed Flows:")
    for flow in FLOW_COMMANDS:
        status = "Allowed" if user.get(flow, "no").lower() == "yes" else "Not Allowed"
        print(f"  - {flow.capitalize():<12}: {status}")

    print("\nType 'help' to see commands. Type 'exit' to quit.\n")

    setup_readline(FLOW_COMMANDS + BUILTIN_COMMANDS)
    ...


    try:
        while True:
            cmd = input("logiclance> ").strip().lower()
            if not cmd:
                continue
            if cmd in ["exit", "quit"]:
                print("👋 Exiting Logic Lance shell. Goodbye!")
                break
            elif cmd in BUILTIN_COMMANDS:
                handle_builtin_command(cmd)
            elif cmd in FLOW_COMMANDS:
                handle_flow_command(cmd, user)
            else:
                subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n👋 Exiting Logic Lance shell. Goodbye!")
    finally:
        save_history()
