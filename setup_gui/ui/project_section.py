from PyQt5.QtWidgets import ( # type: ignore
    QWidget, QLabel, QLineEdit, QVBoxLayout,
    QFormLayout, QComboBox, QPushButton, QMessageBox,
    QGroupBox, QFileDialog, QHBoxLayout
)
from PyQt5.QtGui import QFont # type: ignore
from PyQt5.QtCore import pyqtSignal # type: ignore
import configparser
import os
import shutil




class ProjectSection(QWidget):
    projectSaved = pyqtSignal()

    def __init__(self, available_tools=None, project_name=None):
        self.project_name = project_name
        super().__init__()
        self.available_tools = available_tools or ["Cadence", "Synopsys", "Open Source"]
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Project Setup")
        title.setFont(QFont("Georgia", 16, QFont.Bold))
        layout.addWidget(title)

        # Form Fields
        form_layout = QFormLayout()

        self.tech_node_dropdown = QComboBox()
        self.tech_node_dropdown.addItems(["180nm", "130nm", "65nm", "28nm", "7nm"])

        self.rtl_path_input = QLineEdit()
        self.lef_path_input = QLineEdit()
        self.lib_path_input = QLineEdit()
        self.sdc_path_input = QLineEdit()

        rtl_btn = QPushButton("Browse")
        rtl_btn.clicked.connect(lambda: self.select_directory(self.rtl_path_input))
        lef_btn = QPushButton("Browse")
        lef_btn.clicked.connect(lambda: self.select_directory(self.lef_path_input))
        lib_btn = QPushButton("Browse")
        lib_btn.clicked.connect(lambda: self.select_directory(self.lib_path_input))
        sdc_btn = QPushButton("Browse")
        sdc_btn.clicked.connect(lambda: self.select_directory(self.sdc_path_input))


        self.eda_tool_dropdown = QComboBox()
        self.eda_tool_dropdown.addItems(self.available_tools)

        form_layout.addRow("Technology Node*", self.tech_node_dropdown)

        rtl_layout = QHBoxLayout()
        rtl_layout.addWidget(self.rtl_path_input)
        rtl_layout.addWidget(rtl_btn)
        form_layout.addRow("RTL Directory*", rtl_layout)

        lef_layout = QHBoxLayout()
        lef_layout.addWidget(self.lef_path_input)
        lef_layout.addWidget(lef_btn)
        form_layout.addRow("LEF Directory*", lef_layout)

        lib_layout = QHBoxLayout()
        lib_layout.addWidget(self.lib_path_input)
        lib_layout.addWidget(lib_btn)
        form_layout.addRow("LIB Directory*", lib_layout)

        sdc_layout = QHBoxLayout()
        sdc_layout.addWidget(self.sdc_path_input)
        sdc_layout.addWidget(sdc_btn)
        form_layout.addRow("SDC Directory*", sdc_layout)


        form_layout.addRow("EDA Tool Used*", self.eda_tool_dropdown)

        layout.addLayout(form_layout)

        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def select_directory(self, line_edit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            line_edit.setText(path)

    def is_valid(self):
        def check_dir(path, name, required_exts):
            if not os.path.isdir(path):
                self.error_label.setText(f"{name} path is not a valid directory.")
                return False
            files = os.listdir(path)
            if not files:
                self.error_label.setText(f"{name} directory is empty.")
                return False
            if not any(file.endswith(tuple(required_exts)) for file in files):
                self.error_label.setText(f"{name} must contain at least one {', '.join(required_exts)} file.")
                return False
            return True


        if not check_dir(self.rtl_path_input.text().strip(), "RTL", [".v", ".sv"]):
            return False
        if not check_dir(self.lef_path_input.text().strip(), "LEF", [".lef"]):
            return False
        if not check_dir(self.lib_path_input.text().strip(), "LIB", [".lib"]):
            return False
        if not check_dir(self.sdc_path_input.text().strip(), "SDC", [".sdc"]):
            return False

        if not self.eda_tool_dropdown.currentText().strip():
            self.error_label.setText("EDA tool selection is required.")
            return False

        self.error_label.clear()
        return True




    def copy_files(self, src_dir, dest_dir, extensions):
        if os.path.exists(src_dir):
            os.makedirs(dest_dir, exist_ok=True)
            for file in os.listdir(src_dir):
                if any(file.endswith(ext) for ext in extensions):
                    src_file = os.path.join(src_dir, file)
                    if os.path.isfile(src_file):
                        shutil.copy(src_file, dest_dir)


    def save_project_info(self):
        if not self.is_valid():
            return

        config = configparser.ConfigParser()
        config['PROJECT'] = {
            'tech_node': self.tech_node_dropdown.currentText(),
            'rtl_dir': self.rtl_path_input.text().strip(),
            'lef_dir': self.lef_path_input.text().strip(),
            'lib_dir': self.lib_path_input.text().strip(),
            'sdc_dir': self.sdc_path_input.text().strip(),
            'eda_tool': self.eda_tool_dropdown.currentText()
        }

        config_path = os.path.join("configs", "projects", f"{self.project_name}", "project_paths.cfg")


        with open(config_path, "w") as configfile:
            config.write(configfile)

        data_dir = os.path.join("projects", f"{self.project_name}", "data")
        user_scripts_dir = os.path.join("projects", f"{self.project_name}", "user_scripts")
        self.copy_files(self.rtl_path_input.text().strip(), os.path.join(data_dir, "rtl"), [".v", ".sv"])
        self.copy_files(self.lef_path_input.text().strip(), os.path.join(data_dir, "lef"), [".lef"])
        self.copy_files(self.lib_path_input.text().strip(), os.path.join(data_dir, "lib"), [".lib"])
        self.copy_files(self.sdc_path_input.text().strip(), os.path.join(data_dir, "sdc"), [".sdc"])


        self.projectSaved.emit()


    def get_data(self):
        return {
            "tech_node": self.tech_node_dropdown.currentText(),
            "rtl_dir": self.rtl_path_input.text().strip(),
            "lef_dir": self.lef_path_input.text().strip(),
            "lib_dir": self.lib_path_input.text().strip(),
            "sdc_dir": self.sdc_path_input.text().strip(),
            "eda_tool": self.eda_tool_dropdown.currentText()
        }

    # import os

