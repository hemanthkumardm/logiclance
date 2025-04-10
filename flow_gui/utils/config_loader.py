import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "..", "configs")

def load_setup_config():
    config_path = os.path.join(CONFIG_DIR, "setup_config.json")
    with open(config_path) as f:
        return json.load(f)

def load_flow_config():
    config_path = os.path.join(CONFIG_DIR, "flow_config.json")
    with open(config_path) as f:
        return json.load(f)
