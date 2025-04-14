from PyQt5.QtWidgets import (
    QMainWindow, QStackedWidget, QPushButton, QVBoxLayout, QWidget,
    QHBoxLayout, QLabel, QFileDialog, QMessageBox, QDialog, QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import os
import json
import shutil

from ui.project_section import ProjectSection
from ui.admin_section import AdminSection
from ui.tool_config_section import ToolConfigSection

class MainWindow(QMainWindow):
    def __init__(self, project_name=None):
        super().__init__()
        self.project_name = project_name or "Unnamed_Project"
        self.setWindowTitle(f"Logic Lance - Setup: {self.project_name}")
        self.setGeometry(100, 100, 800, 500)

        self.stack = QStackedWidget()
        self.steps = [
            AdminSection(project_name=self.project_name),
            ProjectSection(project_name=self.project_name),
            ToolConfigSection(project_name=self.project_name)
        ]


        for step in self.steps:
            self.stack.addWidget(step)

        self.current_index = 0
        self.stack.setCurrentIndex(self.current_index)

        # Signal connections
        if isinstance(self.steps[0], AdminSection):
            self.steps[0].adminSaved.connect(self.advance_page)

        if isinstance(self.steps[1], ProjectSection):
            self.steps[1].projectSaved.connect(self.advance_page)

        if isinstance(self.steps[2], ToolConfigSection):
            self.steps[2].toolConfigSaved.connect(self.advance_page)

        # Navigation Buttons
        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self.next_page)

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.prev_page)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setVisible(False)

        self.page_counter = QLabel()
        self.page_counter.setAlignment(Qt.AlignRight)
        self.page_counter.setStyleSheet("font-weight: bold; font-size: 14px; padding-right: 10px;")

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.page_counter)
        nav_layout.addWidget(self.submit_button)
        nav_layout.addWidget(self.next_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        main_layout.addLayout(nav_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_buttons()

    def next_page(self):
        # Step-specific method mapping
        index_method_map = {
            0: "save_admin_info",
            1: "save_project_info",
            2: "save_tool_config",
        }

        method_name = index_method_map.get(self.current_index)
        step = self.steps[self.current_index]

        if method_name and hasattr(step, method_name):
            getattr(step, method_name)()
            return

        self.advance_page()

    def advance_page(self):
        if self.current_index < len(self.steps) - 1:
            self.current_index += 1
            self.stack.setCurrentIndex(self.current_index)
            self.update_buttons()

    def prev_page(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.stack.setCurrentIndex(self.current_index)
            self.update_buttons()

    def update_buttons(self):
        self.back_button.setVisible(self.current_index > 0)
        self.next_button.setVisible(self.current_index < len(self.steps) - 1)
        self.submit_button.setVisible(self.current_index == len(self.steps) - 1)
        self.page_counter.setText(f"{self.current_index + 1} of {len(self.steps)}")

    def submit(self):
        all_data = {}
        for step in self.steps:
            if hasattr(step, "get_data"):
                step_data = step.get_data()
                print(f"[DEBUG] Data from {step.__class__.__name__}: {step_data}")
                if step_data:
                    all_data.update(step_data)

        summary_text = json.dumps(all_data, indent=4)
        print("[DEBUG] Final merged config:", summary_text)

        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Configuration")
        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        text_edit.setPlainText(summary_text)
        text_edit.repaint()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.resize(600, 400)

        if dialog.exec_() != QDialog.Accepted:
            return

        config_dir = os.path.join(os.getcwd(), "configs", "projects", self.project_name)
        os.makedirs(config_dir, exist_ok=True)

        file_path = os.path.join(config_dir, "config.json")

        try:
            with open(file_path, 'w') as f:
                json.dump(all_data, f, indent=4)

            QMessageBox.information(self, "Success", f"Configuration saved to {file_path}")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {e}")
