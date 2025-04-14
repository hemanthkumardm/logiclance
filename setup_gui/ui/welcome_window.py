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
        

        layout.addWidget(welcome_label)


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
