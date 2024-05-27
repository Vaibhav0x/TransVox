import sys
import re
import os
from PyQt5 import QtWidgets, uic
from database import *

# Email validation regex pattern
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def check_ui_files():
    required_files = [r'System Log\login.ui', r'System Log\create.ui', r'System Log\main.ui']
    for file in required_files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Required UI file '{file}' not found.")

class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super(LoginWindow, self).__init__()
        uic.loadUi(r'System Log\login.ui', self)

        self.login_btn.clicked.connect(self.handle_login)
        self.new_acc_btn.clicked.connect(self.open_create_account_window)
        self.forgot_btn.clicked.connect(self.open_reset_credentials_window)   
        
        self.show_btn.pressed.connect(self.show_password)
        self.show_btn.released.connect(self.hide_password)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if verify_user(username, password):
            self.open_main_window(username)
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid username or password')

    def open_create_account_window(self):
        self.create_account_window = CreateAccountWindow()
        self.create_account_window.show()
        self.close()

    def open_reset_credentials_window(self):
        self.reset_credentials_window = ResetCredentialsWindow()
        self.reset_credentials_window.show()
        self.close()

    def open_main_window(self, username):
        self.main_window = MainWindow(username)
        self.main_window.show()
        self.close()

    def show_password(self):
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)

    def hide_password(self):
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

class CreateAccountWindow(QtWidgets.QDialog):
    def __init__(self):
        super(CreateAccountWindow, self).__init__()
        uic.loadUi(r'System Log\create.ui', self)

        self.create_acc_btn.clicked.connect(self.handle_create_account)

    def handle_create_account(self):
        full_name = self.user_name_input.text()
        email = self.user_email_input.text()
        username = self.user_username_input.text()
        password = self.user_password_input.text()
        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid email format')
            return
        
        create_user(full_name, email, username, password)
        QtWidgets.QMessageBox.information(self, 'Success', 'Account created successfully')
        self.open_login_window()

    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

class ResetCredentialsWindow(QtWidgets.QDialog):
    def __init__(self):
        super(ResetCredentialsWindow, self).__init__()
        uic.loadUi(r'System Log\create.ui', self)
        
        self.create_acc_btn.setText("Forgot")
        self.create_acc_btn.clicked.connect(self.handle_reset_credentials)
        self.label1.setText("Enter Old Username:")
        self.user_name_input.setPlaceholderText("Enter old username")
        # self.label2.setText(":")
        # self.fullNameInput.setPlaceholderText("Enter old username")

    def handle_reset_credentials(self):
        old_username = self.user_name_input.text()
        email = self.user_email_input.text()
        new_username = self.user_username_input.text()
        new_password = self.user_password_input.text()

        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid email format')
            return

        if update_user_credentials(old_username, email, new_username, new_password):
            QtWidgets.QMessageBox.information(self, 'Success', 'Credentials reset successfully')
            self.open_login_window()
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid email or old username')

    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username):
        super(MainWindow, self).__init__()
        uic.loadUi(r'System Log\main.ui', self)
        self.username = username

        self.btn1.clicked.connect(self.show_system_logs)
        self.btn2.clicked.connect(self.open_admin_login)
        log_user_activity(self.username, "Logged in")

    def show_system_logs(self):
        logs = get_user_logs()

        self.logsWindow = QtWidgets.QWidget()
        self.logsWindow.setWindowTitle("System Logs")
        layout = QtWidgets.QVBoxLayout()
        
        list_widget = QtWidgets.QListWidget()
        for log in logs:
            list_widget.addItem(f"User: {log[0]}, Time: {log[1]}, Data: {log[2]}")

        layout.addWidget(list_widget)
        self.logsWindow.setLayout(layout)
        self.logsWindow.show()
    
    def open_admin_login(self):
        self.admin_login_window = AdminLoginWindow()
        self.admin_login_window.show()

class AdminLoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super(AdminLoginWindow, self).__init__()
        uic.loadUi(r'System Log\login.ui', self)

        self.login_btn.clicked.connect(self.handle_admin_login)

    def handle_admin_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Assuming admin credentials are hardcoded for simplicity
        if username == "admin" and password == "admin":
            self.open_admin_main_window()
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Invalid admin credentials')

    def open_admin_main_window(self):
        self.admin_main_window = AdminMainWindow()
        self.admin_main_window.show()
        self.close()

class AdminMainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(AdminMainWindow, self).__init__()
        uic.loadUi(r'System Log\admin.ui', self)

        self.del_btn.clicked.connect(self.handle_delete_user)
        self.populate_user_list()

    def populate_user_list(self):
        self.userListWidget.clear()
        users = get_all_users()
        for user in users:
            self.userListWidget.addItem(f"ID: {user[0]}, Username: {user[3]}, Email: {user[2]}")

    def handle_delete_user(self):
        selected_item = self.userListWidget.currentItem()
        if selected_item:
            user_info = selected_item.text()
            user_id = int(user_info.split(",")[0].split(":")[1].strip())
            delete_user(user_id)
            self.populate_user_list()
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'No user selected')
if __name__ == "__main__":
    check_ui_files()
    setup_database()
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
