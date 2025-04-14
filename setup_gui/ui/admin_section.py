from PyQt5.QtWidgets import ( # type: ignore
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QFormLayout
)
from PyQt5.QtGui import QFont, QPalette, QColor # type: ignore
from PyQt5.QtCore import Qt, pyqtSignal # type: ignore
import csv
from shutil import copyfile
import os
import re 
import hashlib
import configparser


REQUIRED_HEADERS = [
    "name", "email", "password", "linting", "synthesis",
    "lec", "pnr", "default_emails", "team"
]

class AdminSection(QWidget):
    adminSaved = pyqtSignal()  # Signal to trigger next page

    def __init__(self, project_name=None):
        self.project_name = project_name
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("QLineEdit, QPushButton { font-size: 13px; }")
        layout = QVBoxLayout()
        title = QLabel("Admin Details")
        title.setFont(QFont("Georgia", 16, QFont.Bold))
        layout.addWidget(title)

        # Admin info form
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.re_pwd_input = QLineEdit()
        self.re_pwd_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Admin Name*", self.name_input)
        form_layout.addRow("Admin Email*", self.email_input)
        form_layout.addRow("Password*", self.pwd_input)
        form_layout.addRow("Re-enter Password*", self.re_pwd_input)
        
        show_pwd_checkbox = QPushButton("👁 Show Passwords") 
        show_pwd_checkbox.setCheckable(True) 
        show_pwd_checkbox.setStyleSheet("margin: 4px;") 
        show_pwd_checkbox.toggled.connect(self.toggle_password_visibility)

        layout.addLayout(form_layout)

        layout.addWidget(show_pwd_checkbox)

        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.error_label)

        # Upload + Download Template Buttons
        btn_layout = QHBoxLayout()

        upload_btn = QPushButton("Upload Employee CSV *")
        upload_btn.clicked.connect(self.upload_csv)

        download_btn = QPushButton("Download CSV Template")
        download_btn.clicked.connect(self.download_template)

        btn_layout.addWidget(upload_btn)
        btn_layout.addWidget(download_btn)

        layout.addLayout(btn_layout)

        # CSV Table View
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)


    def toggle_password_visibility(self, checked): 
        echo_mode = QLineEdit.Normal if checked else QLineEdit.Password 
        self.pwd_input.setEchoMode(echo_mode) 
        self.re_pwd_input.setEchoMode(echo_mode)
       
    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None


    def upload_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV files (*.csv)")
        if not file_name:
            return  # User cancelled

        self.csv_path = file_name
        self.invalid_cells = []  # to track cells with issues
        self.missing_headers = []

        try:
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.invalid_cells = []
            self.missing_headers = []

            with open(file_name, newline='') as csvfile:
                reader = csv.reader(csvfile)
                data = list(reader)

                if not data:
                    raise ValueError("CSV is empty")

                headers = [h.strip().lower() for h in data[0]]
                rows = data[1:]

                self.table.setRowCount(len(rows))
                self.table.resizeColumnsToContents()
                self.table.resizeRowsToContents()
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                self.table.resizeColumnsToContents()

                # Track header issues
                # self.missing_headers = [h for h in REQUIRED_HEADERS if h not in headers]

                for i, row in enumerate(rows):
                    for j in range(len(headers)):
                        try:
                            value = row[j]
                        except IndexError:
                            value = ""

                        item = QTableWidgetItem(value)
                        if value.strip() == "":
                            item.setBackground(Qt.red)
                            self.invalid_cells.append((i, j))
                        self.table.setItem(i, j, item)
                self.table.resizeColumnsToContents()
                self.table.resizeRowsToContents()  
                self.table.setWordWrap(True)
                self.table.setStyleSheet("QTableWidget::item { padding: 4px; }")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read CSV: {e}")

    def is_valid(self):
        csv_loaded = hasattr(self, 'csv_path') and self.csv_path
        if not csv_loaded:
            return False
        if self.missing_headers or self.invalid_cells:
            return False
        return all([
            self.name_input.text().strip(),
            self.email_input.text().strip(),
            self.pwd_input.text().strip(),
            self.re_pwd_input.text().strip()
        ])
    

    def save_table_to_csv(self):

        # Build CSV file path using project name
        save_path = os.path.join("configs", "projects", f"{self.project_name}", "employees.csv")

        try:
            with open(save_path, "w", newline='') as csvfile:
                writer = csv.writer(csvfile)
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)

                # Find password column index
                try:
                    pwd_index = headers.index("password")
                except ValueError:
                    pwd_index = -1  # if not found, skip hashing

                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        value = item.text().strip() if item else ""

                        # Hash password if it's in the password column
                        if col == pwd_index and value:
                            value = self.hash_password(value)

                        row_data.append(value)
                    writer.writerow(row_data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save modified CSV: {e}")


    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()


 # Add at the top if not already imported

    def is_match(self):
        pwd = self.pwd_input.text().strip()
        re_pwd = self.re_pwd_input.text().strip()

        # Check if passwords match
        if pwd != re_pwd:
            self.show_error("Passwords not match.")
            return False

        # Check length
        if len(pwd) < 8:
            self.show_error("Password must be at least 8 characters long.")
            return False

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', pwd):
            self.show_error("Password must contain at least one uppercase letter.")
            return False

        # Check for at least one number
        if not re.search(r'\d', pwd):
            self.show_error("Password must contain at least one number.")
            return False

        # Check for at least one special character
        if not re.search(r'[\W_]', pwd):  # \W = non-alphanumeric, includes special chars
            self.show_error("Password must contain at least one special character.")
            return False
        return True
        


    def show_error(self, msg=None):
        if not msg:
            msg = "Please fill in all required fields marked with *."

        # Add CSV-specific messages
        if hasattr(self, 'missing_headers') and self.missing_headers:
            msg += f"\nMissing CSV headers: {', '.join(self.missing_headers)}"
        if hasattr(self, 'invalid_cells') and self.invalid_cells:
            msg += f"\nEmpty fields highlighted in red."

        self.error_label.setText(msg)
        self.table.setStyleSheet("border: 2px solid red;")



    def clear_error(self):
        self.error_label.clear()

    def save_admin_info(self):
        # First validate the table — this will recheck edited cells
        if not self.validate_table():
            self.show_error("Please correct the highlighted cells in the employee table.")
            return

        if not self.is_valid():
            self.show_error("Please fill all fields correctly.")
            return

        if not self.is_valid_email(self.email_input.text().strip()):
            self.show_error("Invalid email format.")
            return

        if not self.is_match():
            return


        self.clear_error()
        self.save_table_to_csv()  # Save the modified table content
        

        self.adminSaved.emit()



    def validate_table(self):
        self.invalid_cells = []

        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if not item or not item.text().strip():
                    if item is None:
                        item = QTableWidgetItem("")  # create empty item if missing
                        self.table.setItem(row, col, item)
                    item.setBackground(Qt.red)
                    self.invalid_cells.append((row, col))
                else:
                    item.setBackground(Qt.white)  # reset if valid

        return len(self.invalid_cells) == 0


    def extract_csv_data(self):
        employees = []
        for row in range(self.table.rowCount()):
            emp = {}
            for col in range(self.table.columnCount()):
                header = self.table.horizontalHeaderItem(col).text()
                value = self.table.item(row, col)
                emp[header] = value.text() if value else ""
            employees.append(emp)
        return employees

    def get_data(self):
        return {
            "admin_name": self.name_input.text().strip(),
            "admin_email": self.email_input.text().strip(),
            "password": self.hash_password(self.pwd_input.text().strip()),
            "employees": self.extract_csv_data()
        }
    
    def download_template(self):
        try:
            template_path = os.path.join("assets", "employee_template.csv")
            if not os.path.exists(template_path):
                QMessageBox.critical(self, "Error", "CSV Template not found!")
                return

            save_path, _ = QFileDialog.getSaveFileName(self, "Save Template As", "employee_template.csv", "CSV Files (*.csv)")
            if save_path:
                copyfile(template_path, save_path)
                QMessageBox.information(self, "Success", "Template downloaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download template: {e}")
