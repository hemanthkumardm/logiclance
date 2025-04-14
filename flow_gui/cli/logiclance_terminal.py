import os
import readline
import subprocess
import json
import sys
from .commands import run_synthesis, setEdaTool, getEdaTool


HISTORY_FILE = os.path.expanduser("~/.logiclance_history")

def setup_readline():
    readline.parse_and_bind("tab: complete")
    try:
        readline.read_history_file(HISTORY_FILE)
    except FileNotFoundError:
        pass

def save_history():
    try:
        readline.write_history_file(HISTORY_FILE)
    except Exception:
        pass

def source_env_file(env_file):
    """Source a .bin/.sh file and import variables into os.environ"""
    command = f"bash -c 'source {env_file} && env'"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, executable="/bin/bash")
    for line in proc.stdout:
        key, _, value = line.decode().partition("=")
        os.environ[key.strip()] = value.strip()
    proc.communicate()

# Assuming environment variables are set up earlier in the code
def terminal_shell(user, project_name):

    print(f"\n🔓 Welcome to Logic Lance Shell, {user['name'].capitalize()}!")
    print(f" Project       : {os.environ.get('PROJECT_NAME', 'N/A')}")
    print(f" Main Root     : {os.environ.get('MAIN_ROOT', 'N/A')}")
    print(f" Config Root   : {os.environ.get('CONFIG_ROOT', 'N/A')}")
    print(f" RTL Path      : {os.environ.get('RTL_PATH', 'N/A')}")
    print(f" LIB Path      : {os.environ.get('LIB_PATH', 'N/A')}")
    print(f" LEF Path      : {os.environ.get('LEF_PATH', 'N/A')}")
    print(f" SDC Path      : {os.environ.get('SDC_PATH', 'N/A')}")
    print(f" Reports Dir   : {os.environ.get('REPORTS_PATH', 'N/A')}")
    print(f" Scripts Dir   : {os.environ.get('SCRIPTS_PATH', 'N/A')}")
    print(f" Config Path   : {os.environ.get('CONFIG_PATH', 'N/A')}")
    
    config_path = os.path.join("configs", "projects", project_name, "config.json")

    with open(config_path, "r") as f:
        project_config = json.load(f)
    eda_tool = project_config.get("eda_tool", "N/A")

    print(f" EDA Tool      : {eda_tool}")
    print(f" Logic Lance(v): {os.environ.get('VERSION', 'N/A')}")
    print(f" Developer     :  Hemanth Kumar DM, dmhemanthkumar7@gmail.com")

    print("\nType 'help' to see commands. Type 'exit' to quit.\n")

    setup_readline()
    command_counter = 1

    while True:
        cmd = input(f"\033[92mlogiclance:{command_counter}\033[0m> ").strip()
        if not cmd:
            continue

        tokens = cmd.split()
        base_cmd = tokens[0]
        args = tokens[1:]

        if base_cmd in ["exit", "quit"]:
            print("👋 Exiting Logic Lance shell. Goodbye!")
            break

        if base_cmd == "run_synthesis":
            run_synthesis(project_name)
            command_counter += 1
        elif base_cmd == "setEdaTool" and args:
            setEdaTool(args[0])
            command_counter += 1
        elif base_cmd == "getEdaTool":
            print(f"🔍 Current EDA Tool: {get_eda_tool(project_name)}")
            command_counter += 1
        else:
            try:
                subprocess.run(cmd, shell=True)
                command_counter += 1
            except Exception as e:
                print(f"❌ Command failed: {e}")
