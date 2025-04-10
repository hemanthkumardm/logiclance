import sys
from PyQt5.QtWidgets import QApplication # type: ignore
from ui.main_window import MainWindow
from ui.welcome_window import WelcomeWindow
from ui.admin_login import AdminLogin


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.welcome = WelcomeWindow()
        self.main_win = None  # <-- make this persistent
        self.login_win = None

        self.welcome.btn_new_user.clicked.connect(self.open_main_window)
        self.welcome.btn_login.clicked.connect(self.open_login_window)

    def open_main_window(self):
        self.main_win = MainWindow()  # <-- store as self.main_win
        self.main_win.show()
        self.welcome.close()

    def open_login_window(self):
        self.login_win = AdminLogin()
        self.login_win.show()
        self.welcome.close()

    def run(self):
        self.welcome.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = App()
    app.run()
