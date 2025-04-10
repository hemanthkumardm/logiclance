import os
import configparser
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import pyqtSignal

class OrgSection(QWidget):
    orgSaved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        title = QLabel("Organization Details")
        title.setFont(QFont("Georgia", 16, QFont.Bold))
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.org_name_input = QLineEdit()
        self.org_name_input.setPlaceholderText("e.g., LogicLance Inc.")
        form_layout.addRow("Organization Name*", self.org_name_input)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., Bangalore, India")
        form_layout.addRow("Location*", self.location_input)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Optional - email or phone")
        form_layout.addRow("Contact Info", self.contact_input)

        self.error_label = QLabel()
        palette = self.error_label.palette()
        palette.setColor(QPalette.WindowText, QColor("red"))
        self.error_label.setPalette(palette)
        layout.addWidget(self.error_label)

        layout.addLayout(form_layout)
        layout.addStretch()
        self.setLayout(layout)

    def get_data(self):
        return {
            "org_name": self.org_name_input.text().strip(),
            "location": self.location_input.text().strip(),
            "contact": self.contact_input.text().strip()
        }

    def is_valid(self):
        if not self.org_name_input.text().strip():
            self.error_label.setText("Organization name is required.")
            return False
        if not self.location_input.text().strip():
            self.error_label.setText("Location is required.")
            return False
        if self.contact_input.text().strip() and not self.is_valid_contact(self.contact_input.text().strip()):
            self.error_label.setText("Contact info is not valid.")
            return False
        self.error_label.clear()
        return True
    
    def clear_error(self):
        self.error_label.clear()

    def is_valid_contact(self, contact):
        # Simple check: if it contains an '@' symbol, it's treated as an email
        return '@' in contact if contact else True

    def save_org_info(self):
        if not self.is_valid():
            return

        data = self.get_data()
        config = configparser.ConfigParser()
        config["Organization"] = {
            "org_name": data["org_name"],
            "location": data["location"],
            "contact": data["contact"]
        }

        config_path = os.path.join("configs", "org_details.cfg")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # if os.path.exists(config_path):
        #     response = QMessageBox.question(self, "Overwrite File", "The organization details file already exists. Do you want to overwrite it?",
        #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #     if response == QMessageBox.No:
        #         return

        with open(config_path, "w") as configfile:
            config.write(configfile)

        self.orgSaved.emit()
