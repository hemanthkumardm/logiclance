# 🔧 Logic Lance

Logic Lance is an open-source, GUI + CLI-based ASIC design flow automation platform that streamlines setup, user management, and tool execution for a wide range of EDA environments including Cadence, Synopsys, and OpenLane.

---

## 🚀 Features

- 🏗️ Organization & Project Setup via GUI
- 👥 Role-Based Access Control for Users
- 🧰 Multi-Vendor EDA Tool Support
- 📜 Flow Configuration & TCL Scripting
- 🖥️ Interactive CLI Shell with Real-Time Logs
- 🧪 Custom Script Overrides
- 📈 Logs & Reports Per Flow Stage

---

## 🧩 Architecture

Logic Lance is composed of two major modules:

### 1. `setup_gui/` – Organization Setup GUI
Used to configure the ASIC design environment:
- Define organization details
- Add admin & upload employee CSVs
- Assign teams, roles, and permissions
- Create and configure projects
- Select and configure EDA tools with launch.sh
- Output saved to setup_config.json

### 2. `flow_gui/` – Flow Execution UI + CLI
Allows users to run flows:
- Interactive terminal-like CLI shell
- GUI for flow selection and execution
- Uses flow_config.json to resolve tool/script mapping

---

## 📁 Directory Structure

flow_gui/ 
├── cli/ # CLI and shell interface 
├── configs/ # setup_config.json, flow_config.json 
├── scripts/ # Tool-specific TCL scripts 
├── ui/ # Flow execution GUI 
├── utils/ # Internal helpers 
├── logs/ # Execution logs 
├── reports/ # Result artifacts 
├── user_scripts/ # User-defined TCL overrides


---

## 🛠️ Getting Started

### 🔧 Prerequisites

- Python 3.8+
- PyQt5 (for GUI)
- Bash-compatible shell
- Cadence/Synopsys/OpenLane installed and licensed

### 📦 Installation

```bash
git clone https://github.com/<your-org>/logic-lance.git
cd logic-lance
chmod +x logiclance
```

### 🖥️ Launch Setup GUI

`python3 setup_gui/main_window.py`

### 🧪 Launch Flow GUI

`python3 flow_gui/ui/flow_main.py`

### 🧑‍💻 Run Interactive CLI

`./logiclance <username>`

### Example shell:

```
logiclance>
Available flows: synthesis, placement
Enter command: run synthesis
```

### ⚙️ Configuration Files

- setup_config.json – Generated from setup GUI

- flow_config.json – Describes flow steps, tool mappings, dependencies, versions

Sample entry in flow_config.json:

```json
"synthesis": {
  "tools": {
    "cadence": {
      "tool": "genus",
      "script": "scripts/cadence/synthesis.tcl"
    }
  },
  "dependencies": []
}
```

### 🛡️ Security & Access

-     Password-authenticated user login

-     Flows visible per user permission in employee_details.csv

-     Password validation before critical execution

-     Audit logs for all actions

### 📤 Output

-     logs/ – per-stage logs

-     reports/ – flow-generated reports

-     execution transcripts – optionally archived

### 🧭 Roadmap

-     PostgreSQL-based config storage

-     Remote compute node integration

-     Email alerts on job failure/success

-     Visual DAG for flow monitoring

### 👨‍💻 Authors

- Logic Lance Team – Hemanth & Contributors

### 📄 License

- MIT License. See LICENSE file for details.