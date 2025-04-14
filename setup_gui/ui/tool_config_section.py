from PyQt5.QtWidgets import ( # type: ignore # type: ignore
    QWidget, QLabel, QVBoxLayout, QFormLayout, QComboBox, QPushButton,
    QScrollArea, QLineEdit, QFileDialog, QHBoxLayout, QMessageBox, QFrame
)
from PyQt5.QtGui import QFont # type: ignore
from PyQt5.QtCore import pyqtSignal # type: ignore
import json
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem # type: ignore
from PyQt5.QtWidgets import QAbstractItemView # type: ignore

import os
import shutil

class ToolConfigSection(QWidget):
    toolConfigSaved = pyqtSignal()

    def __init__(self, project_name=None):
        self.project_name = project_name
        super().__init__()
        self.tools = ["Cadence", "Synopsys", "Open Source"]
        self.tool_entries = []
        self.tool_table = QTableWidget()
        self.tool_table.setColumnCount(2)
        self.tool_table.setHorizontalHeaderLabels(["EDA Tool", "Launch.sh File"])
        self.tool_table.setWordWrap(True)
        self.tool_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tool_table.horizontalHeader().setStretchLastSection(True)
        self.tool_table.setColumnWidth(0, 150)
        self.tool_table.setColumnWidth(1, 400)
        self.tool_table.setEditTriggers(QTableWidget.NoEditTriggers)


        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        title = QLabel("Tool Configuration")
        title.setFont(QFont("Georgia", 16, QFont.Bold))
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.tool_layout = QVBoxLayout(scroll_content)

        self.add_tool_entry()  # Add first entry

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        add_tool_btn = QPushButton("Add Tool")
        add_tool_btn.clicked.connect(self.add_tool_entry)
        download_template_btn = QPushButton("Download Template")
        download_template_btn.clicked.connect(self.download_template)
        # save_btn = QPushButton("Save Configuration")
        # save_btn.clicked.connect(self.save_config)

        btn_layout.addWidget(add_tool_btn)
        btn_layout.addWidget(download_template_btn)
        # btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Configured Tools:"))
        layout.addWidget(self.tool_table)

        self.setLayout(layout)

    def add_tool_entry(self):
        container = QFrame()
        form = QFormLayout(container)

        tool_dropdown = QComboBox()
        tool_dropdown.addItems(self.tools)

        launch_path_input = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(lambda: self.browse_file(launch_path_input))

        browse_layout = QHBoxLayout()
        browse_layout.addWidget(launch_path_input)
        browse_layout.addWidget(browse_btn)

        form.addRow("EDA Tool", tool_dropdown)
        form.addRow("Launch.sh File", browse_layout)

        self.tool_layout.addWidget(container)
        self.tool_entries.append({
            "tool_dropdown": tool_dropdown,
            "launch_input": launch_path_input
        })
        self.update_tool_table()


    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select launch.sh", "", "Shell Scripts (*.sh)")
        if file_path:
            line_edit.setText(file_path)

    def download_template(self):
        template_path = os.path.join("assets", "launch.sh")

        if not os.path.exists(template_path):
            QMessageBox.critical(self, "Error", "Template file not found in assets directory.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Template", "launch_template.sh", "Shell Scripts (*.sh)")
        if save_path:
            try:
                shutil.copy(template_path, save_path)
                QMessageBox.information(self, "Saved", "Template saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save template: {str(e)}")


    def get_data(self):
        config_dir = os.path.join(os.getcwd(), "configs", "projects", f"{self.project_name}")
        os.makedirs(config_dir, exist_ok=True)

        tool_config = []

        for idx, entry in enumerate(self.tool_entries):
            tool = entry["tool_dropdown"].currentText()
            launch_path = entry["launch_input"].text().strip()

            if launch_path and os.path.exists(launch_path):
                safe_tool_name = tool.lower().replace(" ", "_")
                dest_filename = f"{safe_tool_name}_launch.sh"

                dest_path = os.path.join(config_dir, dest_filename)
                try:
                    shutil.copy(launch_path, dest_path)
                except Exception as e:
                    print(f"Failed to copy {launch_path} → {dest_path}: {e}")
                    dest_path = ""
            else:
                dest_path = ""

            tool_config.append({
                "tool": tool,
                "launch_sh_path": dest_path
            })

        self.update_tool_table()
        return {"tool_config": tool_config}


    def update_tool_table(self):
        self.tool_table.setRowCount(0)  # Clear existing rows

        for entry in self.tool_entries:
            tool = entry["tool_dropdown"].currentText()
            launch_path = entry["launch_input"].text().strip()

            launch_content = ""
            if os.path.exists(launch_path):
                try:
                    with open(launch_path, "r") as f:
                        launch_content = f.read()
                except Exception as e:
                    launch_content = f"Error reading file: {e}"

            row_position = self.tool_table.rowCount()
            self.tool_table.insertRow(row_position)
            self.tool_table.setItem(row_position, 0, QTableWidgetItem(tool))
            self.tool_table.setItem(row_position, 1, QTableWidgetItem(launch_content))
