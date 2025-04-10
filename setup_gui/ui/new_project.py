import sys
import os
import json
import csv
import re
import shutil
from PyQt5.QtWidgets import (  # type: ignore
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QLineEdit, QComboBox, QLabel
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class NewProjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Project - Logic Lance")
        self.setGeometry(100, 100, 1000, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Project name and dates
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Project Name")
        layout.addWidget(QLabel("Project Name"))
        layout.addWidget(self.project_name_input)

        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("Start Date (YYYY-MM-DD)")
        layout.addWidget(QLabel("Start Date"))
        layout.addWidget(self.start_date_input)

        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("End Date (YYYY-MM-DD)")
        layout.addWidget(QLabel("End Date"))
        layout.addWidget(self.end_date_input)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name or email")
        self.search_bar.textChanged.connect(self.search_table)
        search_layout.addWidget(self.search_bar)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Name", "Email", "Password", "Linting",
            "Synthesis", "LEC", "PNR", "Default Emails", "Team"
        ])
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        self.clone_button = QPushButton("Clone Selected Row")
        self.clone_button.clicked.connect(self.clone_selected_row)
        button_layout.addWidget(self.clone_button)

        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_empty_row)
        button_layout.addWidget(self.add_row_button)

        self.delete_row_button = QPushButton("Delete Selected Row")
        self.delete_row_button.clicked.connect(self.delete_selected_row)
        button_layout.addWidget(self.delete_row_button)

        self.save_button = QPushButton("Save Project JSON")
        self.save_button.clicked.connect(self.save_changes_to_json)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.employee_data = []
        self.populate_table()

    def populate_table(self):
        self.table.setRowCount(0)
        for employee in self.employee_data:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for col, key in enumerate(["name", "email", "password", "linting", "synthesis", "lec", "pnr", "default_emails", "team"]):
                if key in ["linting", "synthesis", "lec", "pnr"]:
                    combo = QComboBox()
                    combo.addItems(["yes", "no"])
                    combo.setCurrentText(employee.get(key, "no"))
                    self.table.setCellWidget(row, col, combo)
                else:
                    item = QTableWidgetItem(employee.get(key, ""))
                    if key == "email" and not self.is_valid_email(employee.get(key, "")):
                        item.setBackground(QColor("red"))
                    self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()

    def is_valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def clone_selected_row(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Warning", "No row selected.")
            return

        row_data = {}
        for col, key in enumerate(["name", "email", "password", "linting", "synthesis", "lec", "pnr", "default_emails", "team"]):
            if key in ["linting", "synthesis", "lec", "pnr"]:
                widget = self.table.cellWidget(selected, col)
                row_data[key] = widget.currentText()
            else:
                item = self.table.item(selected, col)
                row_data[key] = item.text() if item else ""

        self.employee_data.append(row_data)
        self.populate_table()

    def add_empty_row(self):
        row_data = {key: "" for key in ["name", "email", "password", "linting", "synthesis", "lec", "pnr", "default_emails", "team"]}
        self.employee_data.append(row_data)
        self.populate_table()

    def delete_selected_row(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.employee_data.pop(selected)
            self.populate_table()
        else:
            QMessageBox.warning(self, "Warning", "No row selected.")

    def save_changes_to_json(self):
        updated_employees = []
        for row in range(self.table.rowCount()):
            employee = {}
            for col, key in enumerate(["name", "email", "password", "linting", "synthesis", "lec", "pnr", "default_emails", "team"]):
                if key in ["linting", "synthesis", "lec", "pnr"]:
                    widget = self.table.cellWidget(row, col)
                    employee[key] = widget.currentText()
                else:
                    item = self.table.item(row, col)
                    employee[key] = item.text() if item else ""
            updated_employees.append(employee)

        self.employee_data = updated_employees

        project_name = self.project_name_input.text().strip().replace(" ", "_")
        if not project_name:
            QMessageBox.warning(self, "Error", "Project name is required to save.")
            return

        project_info = {
            "project_name": self.project_name_input.text(),
            "start_date": self.start_date_input.text(),
            "end_date": self.end_date_input.text(),
            "employees": self.employee_data
        }

        # Ensure configs directory exists
        os.makedirs("configs", exist_ok=True)

        # Save JSON file
        save_path = os.path.join("configs", f"{project_name}.json")
        with open(save_path, "w") as f:
            json.dump(project_info, f, indent=4)

        # Copy supporting folders into configs/project_name
        dest_dir = os.path.join("configs", project_name)
        os.makedirs(dest_dir, exist_ok=True)

        folders_to_copy = ["flow_gui", "data", "logs", "reports", "outputs"]
        for folder in folders_to_copy:
            src = os.path.join(os.getcwd(), folder)
            dst = os.path.join(dest_dir, folder)
            if os.path.exists(src):
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

        QMessageBox.information(self, "Success", f"Saved to configs/{project_name}.json and copied folders.")


    def search_table(self, text):
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            email_item = self.table.item(row, 1)
            if name_item and email_item:
                match = text.lower() in name_item.text().lower() or text.lower() in email_item.text().lower()
                self.table.setRowHidden(row, not match)


    def copy_to_project_folder(self):
        project_name = self.project_name_input.text().strip().replace(" ", "_")
        if not project_name:
            QMessageBox.warning(self, "Error", "Project name is required to copy project folders.")
            return

        dest_share_dir = os.path.join(os.getcwd(), project_name)
        os.makedirs(dest_share_dir, exist_ok=True)

        folders_to_copy = ["flow_gui", "data", "logs", "reports", "outputs"]
        for folder in folders_to_copy:
            src = os.path.join(os.getcwd(), folder)
            dst = os.path.join(dest_share_dir, folder)

            if os.path.exists(src):
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

        QMessageBox.information(self, "Success", f"Project folders copied to {dest_share_dir}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewProjectWindow()
    window.show()
    sys.exit(app.exec_())
