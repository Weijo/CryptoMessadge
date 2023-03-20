from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class LoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Chat Messager')

        # set window size and position
        self.setGeometry(100, 100, 600, 500)

        # create header label
        header = QLabel('Crypto Messadge Login Page')
        header.setStyleSheet('font-size: 20pt; font-weight: bold;')

        # create username label and text field
        username_label = QLabel('Username:')
        self.username = QLineEdit()
        self.username.setFixedWidth(300)

        # create password label and text field
        password_label = QLabel('Password:')
        self.password = QLineEdit()
        self.password.setFixedWidth(300)
        self.password.setEchoMode(QLineEdit.Password)

        # create login button
        login_button = QPushButton('Login')
        login_button.clicked.connect(self.login)

        # create register button
        register_button = QPushButton('Register')
        register_button.clicked.connect(self.register)

        # create vertical layout for header
        layout = QVBoxLayout()
        layout.addWidget(header)

        # create horizontal layout for username label and field
        username_layout = QHBoxLayout()

        # add username label and field to username layout
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username)
        username_layout.setContentsMargins(50, 50, 50, 0)
        layout.addLayout(username_layout)

        # create horizontal layout for password label and field
        password_layout = QHBoxLayout()

        # add password label and field to password layout
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password)
        password_layout.setContentsMargins(50, 0, 50, 50)
        layout.addLayout(password_layout)

        # add login and register button to layout
        layout.addWidget(login_button)
        layout.addWidget(register_button)
        layout.setContentsMargins(50, 50, 50, 50)

        self.setLayout(layout)

    def login(self):
        username = self.username.text()
        password = self.password.text()
        print('Login button clicked!')

    def register(self):
        print('Register button clicked!')

if __name__ == '__main__':
    app = QApplication([])
    login_widget = LoginWidget()
    login_widget.show()
    app.exec_()
