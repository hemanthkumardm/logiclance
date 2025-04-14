import os
import json
import subprocess

def run_synthesis(current_project):
    print("🚀 Running synthesis flow...")

    CONFIG_ROOT = os.environ.get("CONFIG_ROOT")
    LOGIC_LANCE_ROOT = os.environ.get("LOGICLANCE_ROOT")

    if not CONFIG_ROOT or not LOGIC_LANCE_ROOT:
        print("❌ CONFIG_ROOT or LOGIC_LANCE_ROOT environment variable not set.")
        return

    # Load project config
    project_config_path = os.path.join(CONFIG_ROOT, "config.json")
    try:
        with open(project_config_path, "r") as f:
            project_config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Project config not found at {project_config_path}")
        return

    eda_tool = getEdaTool()
    if not eda_tool:
        print("❌ No EDA tool set in session or project config.")
        return
    eda_tool = eda_tool.lower()

    if not eda_tool:
        print("❌ No EDA tool set in project config.")
        return

    # Load flow setup config
    flow_setup_path = os.path.join(LOGIC_LANCE_ROOT, "configs", "flow_setup.json")
    try:
        with open(flow_setup_path, "r") as f:
            flow_config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Flow setup config not found at {flow_setup_path}")
        return

    # Get the script path from flow setup
    try:
        synthesis_tool_info = flow_config["flows"]["synthesis"]["tools"][eda_tool]
        script_path = os.path.join(LOGIC_LANCE_ROOT, synthesis_tool_info["script"])
    except KeyError:
        print(f"❌ No synthesis script configured for tool '{eda_tool}' in flow_setup.json.")
        return

    print(f"🔧 Using EDA Tool      : {eda_tool}")
    print(f"📂 Synthesis Script   : {script_path}")

    try:
        if eda_tool == "cadence":
            # Run using Genus
            cmd = f"genus -f {script_path}"
        elif eda_tool == "openlane":
            # Run using yosys (could be customized per OpenLane flow specifics)
            cmd = f"yosys {script_path}"
        else:
            print(f"❌ Unknown or unsupported tool '{eda_tool}' for synthesis.")
            return

        subprocess.run(cmd, shell=True, check=True, executable="/bin/bash")
        print("✅ Synthesis completed.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Synthesis failed with error: {e}")


session_eda_tool = None

def setEdaTool(tool_name):
    global session_eda_tool

    CONFIG_ROOT = os.environ.get("CONFIG_ROOT")
    if not CONFIG_ROOT:
        print("❌ CONFIG_ROOT environment variable not set.")
        return

    config_path = os.path.join(CONFIG_ROOT, "config.json")
    if not os.path.exists(config_path):
        print(f"❌ Project config not found at {config_path}")
        return

    tool_name = tool_name.lower()

    # Handle alias
    if tool_name == "open_source":
        tool_name = "openlane"

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        if tool_name == "openlane":
            session_eda_tool = tool_name
            print(f"✅ Session EDA Tool set to: {tool_name}")
        else:
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
    except:
        return None
