import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt, QSize


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Welcome to Logic Lance")
        self.setGeometry(100, 100, 800, 400)  # Adjust window size for better proportions

        # Load background image
        pixmap = QPixmap("setup_gui/assets/vlsi-design-services.jpg")  # Change path accordingly
        if not pixmap.isNull():
            self.setGeometry(100, 100, pixmap.width(), pixmap.height())
        
        # Set background image
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(pixmap))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        welcome_label = QLabel("Welcome to\nLogicLance")
        welcome_label.setFont(QFont("Georgia", 25, QFont.Bold))
        welcome_label.setStyleSheet("color: white;") 
        welcome_label.setAlignment(Qt.AlignLeft)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Reduce space between buttons
        
        # Create buttons with a cleaner look
        new_user_button = QPushButton("New User")
        new_user_button.setFont(QFont("Georgia", 14))
        new_user_button.setFixedSize(QSize(120, 40))  # Reduce button size
        new_user_button.setStyleSheet(
            "color: black; background-color: white; border-radius: 5px;"
        )
        new_user_button.setCursor(Qt.PointingHandCursor)
        
        login_button = QPushButton("Login")
        login_button.setFont(QFont("Georgia", 14))
        login_button.setFixedSize(QSize(120, 40))  # Reduce button size
        login_button.setStyleSheet(
            "color: black; background-color: white; border-radius: 5px;"
        )
        login_button.setCursor(Qt.PointingHandCursor)
        
        # Add buttons to layout
        button_layout.addWidget(new_user_button)
        button_layout.addWidget(login_button)
        
        layout.addWidget(welcome_label)
        layout.addLayout(button_layout)

        # Footer Section with same width but smaller height
        footer = QFrame()
        footer.setStyleSheet("background-color: black; border: 2px solid white; padding: 2px; border-radius: 5px;")
        footer.setFixedHeight(30)  # Reduce height to make it smaller
        footer_layout = QVBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)  # Reduce extra padding

        owner_label = QLabel("Developed by Hemanth")
        owner_label.setFont(QFont("Georgia", 10, QFont.Bold))  # Adjust font size to match compact design
        owner_label.setStyleSheet("color: white;")
        owner_label.setAlignment(Qt.AlignCenter)

        footer_layout.addWidget(owner_label)
        footer.setLayout(footer_layout)

        # Center footer
        footer_container = QHBoxLayout()
        footer_container.addStretch()
        footer_container.addWidget(footer)
        footer_container.addStretch()

        layout.addLayout(footer_container)

        self.setLayout(layout)

        # Correct variable names here
        self.btn_new_user = new_user_button
        self.btn_login = login_button
