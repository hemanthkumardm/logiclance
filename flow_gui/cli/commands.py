import os
import json
import subprocess

def run_synthesis(script_flag=None, custom_script_path=None):
    print("🚀 Running synthesis flow...")

    CONFIG_ROOT = os.environ.get("CONFIG_ROOT")
    LOGICLANCE_ROOT = os.environ.get("LOGICLANCE_ROOT")

    if not CONFIG_ROOT or not LOGICLANCE_ROOT:
        print("❌ CONFIG_ROOT or LOGICLANCE_ROOT environment variable not set.")
        return

    eda_tool = getEdaTool()
    if not eda_tool:
        print("❌ No EDA tool set in session or project config.")
        return
    eda_tool = eda_tool.lower()

    # Determine script path
    if script_flag == "-f" and custom_script_path:
        # Use custom user-provided script
        script_path = os.path.abspath(custom_script_path)
        if not os.path.exists(script_path):
            print(f"❌ Provided script not found at: {script_path}")
            return
    else:
        # Load script from flow_setup.json
        flow_setup_path = os.path.join(LOGICLANCE_ROOT, "configs", "flow_setup.json")
        try:
            with open(flow_setup_path, "r") as f:
                flow_config = json.load(f)
            synthesis_tool_info = flow_config["flows"]["synthesis"]["tools"][eda_tool]
            script_path = os.path.join(LOGICLANCE_ROOT, synthesis_tool_info["script"])
        except (FileNotFoundError, KeyError):
            print(f"❌ Could not locate synthesis script for '{eda_tool}' in flow_setup.json.")
            return

    
        print(f"🔧 Using EDA Tool      : {eda_tool}")
        print(f"📂 Synthesis Script   : {script_path}")

        # Set 'order' if cadence tool is used
        if eda_tool == "cadence":
            synthesis_order = flow_config["flows"]["synthesis"].get("order", [])
            os.environ["order"] = ",".join(synthesis_order)
            print(f"📜 Script execution order: {os.environ['order']}")


        try:
            if eda_tool == "cadence":
                cmd = f"genus -f {script_path}"
            elif eda_tool == "openlane":
                cmd = f"yosys {script_path}"
            elif eda_tool == "synopsys":
                cmd = f"dc_shell -f {script_path}"
            else:
                print(f"❌ Unsupported EDA tool: {eda_tool}")
                return

            subprocess.run(cmd, shell=True, check=True, executable="/bin/bash")
            print("✅ Synthesis completed.")

        except subprocess.CalledProcessError as e:
            print(f"❌ Synthesis failed with error: {e}")




session_eda_tool = None

def setEdaTool(tool_name, command=None):
    COMMAND_HELP = {
        "run_synthesis": "Run synthesis flow for the project.",
        "setEdaTool <tool_name>": "Set the EDA tool to use (e.g., openlane, cadence).",
        "getEdaTool": "Show the current EDA tool in use.",
        "exit / quit": "Exit the Logic Lance CLI shell.",
        "help": "Show this help message.",
    }

    # Show help if requested
    if command == "help":
        for cmd, desc in COMMAND_HELP.items():
            print(f"📌 {cmd.ljust(25)} - {desc}")
        return

    global session_eda_tool

    tool_name = tool_name.lower()

    # Handle alias
    if tool_name == "open_source":
        tool_name = "openlane"

    # If user sets to openlane, skip config check
    if tool_name == "openlane":
        session_eda_tool = tool_name
        print(f"✅ Session EDA Tool set to: {tool_name}")
        return

    # For other tools, validate from config.json
    CONFIG_ROOT = os.environ.get("CONFIG_ROOT")
    if not CONFIG_ROOT:
        print("❌ CONFIG_ROOT environment variable not set.")
        return

    config_path = os.path.join(CONFIG_ROOT, "config.json")
    if not os.path.exists(config_path):
        print(f"❌ Project config not found at {config_path}")
        return

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        # Check if the tool is present in the config
        tool_exists = any(tool["tool"].lower() == tool_name for tool in config.get("tool_config", []))
        if tool_exists:
            session_eda_tool = tool_name
            print(f"✅ Session EDA Tool set to: {tool_name}")
        else:
            print(f"❌ Tool '{tool_name}' not found in tool_config. Please add it to your config.")

    except Exception as e:
        print(f"❌ Error setting EDA tool: {e}")


def getEdaTool():
    global session_eda_tool
    if session_eda_tool:
        return session_eda_tool.lower()

    CONFIG_ROOT = os.environ.get("CONFIG_ROOT")
    if not CONFIG_ROOT:
        return None

    config_path = os.path.join(CONFIG_ROOT, "config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("eda_tool", "").lower()
    except Exception:
        return None
    


def project_info(project_name):
    CONFIG_ROOT = os.environ.get("CONFIG_ROOT")
    LL_ROOT = os.environ.get("LOGICLANCE_ROOT", os.path.expanduser("~/Logic_Lance"))

    info = {
        "Project": project_name,
        "MAIN_ROOT": LL_ROOT,
        "RTL_PATH": os.path.join(LL_ROOT, "projects", project_name, "data", "rtl"),
        "LIB_PATH": os.path.join(LL_ROOT, "projects", project_name, "data", "lib"),
        "LEF_PATH": os.path.join(LL_ROOT, "projects", project_name, "data", "lef"),
        "SDC_PATH": os.path.join(LL_ROOT, "projects", project_name, "data", "sdc"),
        "REPORTS_PATH": os.path.join(LL_ROOT, "projects", project_name, "reports"),
        "OUTPUTS_PATH": os.path.join(LL_ROOT, "projects", project_name, "outputs"),
        "LOGS_PATH": os.path.join(LL_ROOT, "projects", project_name, "logs"),
        "Developer": "Hemanth Kumar DM, dmhemanthkumar7@gmail.com"
    }

    print("\n📌 Project Configuration")
    print("-" * 60)
    for key, value in info.items():
        print(f"{key.ljust(15)}: {value}")
    print("-" * 60)

