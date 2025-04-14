import sys
import os
import json
import csv
import re
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import ( # type: ignore
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QLineEdit, QComboBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class ModifyProjectWindow(QWidget):
    def __init__(self, project_name=None):
        super().__init__()
        self.project_name = project_name
        self.setWindowTitle("Modify Project")

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

        # Data directory file management
        self.data_dir = os.path.join("projects", f"{self.project_name}", "data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.file_list = QTableWidget()
        self.file_list.setColumnCount(1)
        self.file_list.setHorizontalHeaderLabels(["Data Directory Files"])
        self.refresh_file_list()
        layout.addWidget(self.file_list)

        file_button_layout = QHBoxLayout()

        self.upload_btn = QPushButton("📤 Add File")
        self.upload_btn.clicked.connect(self.upload_file)
        file_button_layout.addWidget(self.upload_btn)

        self.delete_btn = QPushButton("🗑️ Delete Selected File")
        self.delete_btn.clicked.connect(self.delete_selected_file)
        file_button_layout.addWidget(self.delete_btn)

        layout.addLayout(file_button_layout)

        self.file_list.cellDoubleClicked.connect(self.toggle_folder_expansion)
        self.expanded_dirs = set()  # Track expanded directories

        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        self.config_path = os.path.join("configs", "projects", f"{self.project_name}", "config.json")
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


    
    def refresh_file_list(self):
        self.file_list.setRowCount(0)
        self.populate_file_list(self.data_dir, indent=0)

    def populate_file_list(self, directory, indent=0):
        try:
            entries = sorted(os.listdir(directory))
            for entry in entries:
                full_path = os.path.join(directory, entry)
                row = self.file_list.rowCount()
                self.file_list.insertRow(row)

                if os.path.isdir(full_path):
                    display_text = "    " * indent + f"[DIR] {entry}"
                else:
                    display_text = "    " * indent + entry

                item_widget = QTableWidgetItem(display_text)
                item_widget.setData(Qt.UserRole, full_path)
                item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.file_list.setItem(row, 0, item_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading directory: {e}")



    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if file_path:
            try:
                dest_path = os.path.join(self.data_dir, os.path.basename(file_path))
                if os.path.exists(dest_path):
                    QMessageBox.warning(self, "File Exists", "File already exists. Choose another file.")
                    return
                with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
                QMessageBox.information(self, "Success", "File uploaded successfully.")
                self.refresh_file_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload file: {e}")

    def delete_selected_file(self):
        selected_row = self.file_list.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "No file or folder selected.")
            return

        file_item = self.file_list.item(selected_row, 0)
        if not file_item:
            return

        label = file_item.text()
        if label.startswith("[DIR] "):
            name = label[6:]
        else:
            name = label

        path = os.path.join(self.data_dir, name)

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.refresh_file_list()
                QMessageBox.information(self, "Deleted", f"{name} has been deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")


    def toggle_folder_expansion(self, row, column):
        item = self.file_list.item(row, column)
        if not item:
            return

        path = item.data(Qt.UserRole)
        if not os.path.isdir(path):
            return  # only folders can be expanded

        # Check if already expanded
        if path in self.expanded_dirs:
            self.collapse_folder(path)
            self.expanded_dirs.remove(path)
        else:
            self.expand_folder(path, row, indent=self.get_indent_level(item) + 1)
            self.expanded_dirs.add(path)

    def get_indent_level(self, item):
        text = item.text()
        return (len(text) - len(text.lstrip())) // 4  # 4 spaces per indent

    def expand_folder(self, folder_path, row_index, indent):
        try:
            entries = sorted(os.listdir(folder_path))
            for i, entry in enumerate(entries):
                full_path = os.path.join(folder_path, entry)
                self.file_list.insertRow(row_index + 1 + i)

                if os.path.isdir(full_path):
                    display_text = "    " * indent + f"[DIR] {entry}"
                else:
                    display_text = "    " * indent + entry

                item_widget = QTableWidgetItem(display_text)
                item_widget.setData(Qt.UserRole, full_path)
                item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.file_list.setItem(row_index + 1 + i, 0, item_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to expand folder: {e}")

    def collapse_folder(self, folder_path):
        rows_to_remove = []
        for row in range(self.file_list.rowCount()):
            item = self.file_list.item(row, 0)
            if not item:
                continue
            item_path = item.data(Qt.UserRole)
            if item_path and item_path.startswith(folder_path) and item_path != folder_path:
                rows_to_remove.append(row)

        # Remove from bottom to avoid row shifting issues
        for row in reversed(rows_to_remove):
            self.file_list.removeRow(row)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModifyProjectWindow()
    window.show()
    sys.exit(app.exec_())