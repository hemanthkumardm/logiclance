import sys
import json
import os
import hashlib
from PyQt5.QtWidgets import (  # type: ignore
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt  # type: ignore
from ui.modify_project import ModifyProjectWindow
from ui.new_project import NewProjectWindow


class PostLoginWindow(QWidget):
    def __init__(self, project_name=None):
        super().__init__()
        self.setWindowTitle("Select Action")
        self.setGeometry(300, 300, 350, 160)


        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.modify_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def modify_project(self):
        self.modify_window = ModifyProjectWindow()
        self.modify_window.show()
        self.close()



class AdminLogin(QWidget):
    def __init__(self, project_name=None):
        super().__init__()
        self.project_name = project_name
        self.setWindowTitle("Admin Login")
        self.setGeometry(200, 200, 350, 180)

        self.username_label = QLabel("Admin Name:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter admin username")

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_password_btn = QPushButton("Show")
        self.toggle_password_btn.setCheckable(True)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)

        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_btn)

        self.login_button = QPushButton("🔐 Login")
        self.login_button.clicked.connect(self.validate_credentials)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addLayout(password_layout)
        layout.addWidget(self.login_button)

        # Styling
        self.login_button.setStyleSheet("background-color: #0275d8; color: white; font-weight: bold; padding: 8px;")
        self.toggle_password_btn.setStyleSheet("padding: 5px;")
        self.username_input.setFocus()

        # Enable login on pressing Enter
        self.password_input.returnPressed.connect(self.validate_credentials)
        self.username_input.returnPressed.connect(self.validate_credentials)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.toggle_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("Show")

    def validate_credentials(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        config_path = os.path.join("configs", "projects", f"{self.project_name}", "config.json")
        if not os.path.exists(config_path):
            QMessageBox.critical(self, "Error", "config.json not found.")
            return

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config: {e}")
            return

        admin_name = config.get("admin_name", "")
        stored_password = config.get("password", "")

        hashed_input = hashlib.sha256(password.encode()).hexdigest()

        if username == admin_name and hashed_input == stored_password:
            self.launch_post_login_options()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")


    def launch_post_login_options(self):
        self.close()
        self.modify_window = ModifyProjectWindow(project_name=self.project_name)
        self.modify_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = AdminLogin()
    login_window.show()
    sys.exit(app.exec_())
