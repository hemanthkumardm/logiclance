import sys
import os
import json
import csv
import re
from PyQt5.QtWidgets import ( # type: ignore
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QLineEdit, QComboBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class ModifyProjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modify Project - Logic Lance")
        self.setGeometry(100, 100, 1000, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

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

        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes_to_json)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        self.config_path = os.path.join("configs", "setup_config.json")
        if not os.path.exists(self.config_path):
            QMessageBox.critical(self, "Error", "setup_config.json not found.")
            return

        with open(self.config_path, "r") as f:
            self.config_data = json.load(f)

        self.employee_data = self.config_data.get("employees", [])
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
                    combo.setCurrentText(employee[key])
                    self.table.setCellWidget(row, col, combo)
                else:
                    item = QTableWidgetItem(employee[key])
                    if key == "email" and not self.is_valid_email(employee[key]):
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

        self.config_data["employees"] = updated_employees

        with open(self.config_path, "w") as f:
            json.dump(self.config_data, f, indent=4)

        QMessageBox.information(self, "Success", "Changes saved to setup_config.json")

    def search_table(self, text):
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            email_item = self.table.item(row, 1)
            if name_item and email_item:
                match = text.lower() in name_item.text().lower() or text.lower() in email_item.text().lower()
                self.table.setRowHidden(row, not match)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModifyProjectWindow()
    window.show()
    sys.exit(app.exec_())