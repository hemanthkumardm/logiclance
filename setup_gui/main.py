import sys
import os
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox  # type: ignore
from PyQt5.QtCore import QTimer  # type: ignore
from ui.main_window import MainWindow
from ui.welcome_window import WelcomeWindow
from ui.admin_login import AdminLogin
import json


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.project_name = ""
        self.project_exists = False

        self.welcome = WelcomeWindow()
        self.main_win = None
        self.login_win = None

        # Show splash-like welcome window
        self.welcome.show()

        # After 1 second, prompt for project name
        QTimer.singleShot(1000, self.prompt_project_name)

    def prompt_project_name(self):
        self.welcome.close()

        while True:
            name, ok = QInputDialog.getText(None, "Enter Project Name", "Project Name:")
            if not ok:
                sys.exit(0)

            name = name.strip()
            if not name:
                continue

            self.project_name = name
            project_dir = os.path.join("configs", "projects", self.project_name)

            if os.path.exists(project_dir):
                choice = QMessageBox.question(
                    None,
                    "Project Exists",
                    f"The project '{self.project_name}' already exists.\nDo you want to edit it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if choice == QMessageBox.Yes:
                    self.project_exists = True
                    break
                else:
                    continue  # Re-prompt for a new name
            else:
                try:
                    os.makedirs(project_dir, exist_ok=True)
                    self.project_exists = False
                    break
                except Exception as e:
                    QMessageBox.critical(None, "Error", f"Failed to create project directory: {e}")
                    sys.exit(1)

        self.handle_redirect()

    def handle_redirect(self):
        # Always update config and env after project name is finalized
        update_project_flow_config(self.project_name)

        if self.project_exists:
            self.open_login_window()
        else:
            self.open_main_window()


    def open_main_window(self):
        self.main_win = MainWindow(project_name=self.project_name)
        self.main_win.show()

    def open_login_window(self):
        self.login_win = AdminLogin(project_name=self.project_name)
        self.login_win.show()

    def run(self):
        sys.exit(self.app.exec_())



    
# Keep these outside the class
def generate_env_sh(project_name):
    project_root = os.path.abspath(f"projects/{project_name}")
    config_root = os.path.abspath(f"configs/projects/{project_name}")
    env_path = os.path.join(project_root, f".env_{project_name}.sh")

    paths = {
        "PROJECT_NAME": project_name,
        "MAIN_ROOT": os.path.abspath("."),
        "CONFIG_ROOT": config_root,
        "RTL_PATH": os.path.join(project_root, "data", "rtl"),
        "LIB_PATH": os.path.join(project_root, "data", "lib"),
        "LEF_PATH": os.path.join(project_root, "data", "lef"),
        "SDC_PATH": os.path.join(project_root, "data", "sdc"),
        "LOG_PATH": os.path.join(project_root, "logs"),
        "OUTPUTS_PATH": os.path(project_root, "outputs"),
        "REPORTS_PATH": os.path.join(project_root, "reports"),
        "CONFIG_PATH": os.path.join(config_root, "config.json")
    }

    os.makedirs(project_root, exist_ok=True)

    # Write to .env file
    with open(env_path, "w") as f:
        for key, path in paths.items():
            f.write(f"export {key}={path}\n")

    # Export to os.environ
    for key, path in paths.items():
        os.environ[key] = path

    return paths, env_path


def update_project_flow_config(project_name):
    paths, _ = generate_env_sh(project_name)

    setup_path = "configs/flow_setup.json"
    with open(setup_path, "r") as f:
        flow_config = json.load(f)

    flow_config["project_name"] = project_name
    flow_config["rtl_paths"] = [paths["RTL_PATH"]]
    flow_config["lib_paths"] = [paths["LIB_PATH"]]
    flow_config["lef_paths"] = [paths["LEF_PATH"]]
    flow_config["sdc_path"] =  [paths["SDC_PATH"]]
    flow_config["log_path"] = paths["LOG_PATH"]
    flow_config["outputs_path"] = paths["OUTPUTS_PATH"]
    flow_config["reports_path"] = paths["REPORTS_PATH"]
    flow_config["config_path"] = paths["CONFIG_PATH"]



    project_config_dir = f"projects/{project_name}"
    os.makedirs(project_config_dir, exist_ok=True)

    project_config_path = os.path.join(project_config_dir, "config.json")
    with open(project_config_path, "w") as f:
        json.dump(flow_config, f, indent=2)

    print(f"✅ Updated config saved to {project_config_path}")



if __name__ == "__main__":
    app = App()
    app.run()
