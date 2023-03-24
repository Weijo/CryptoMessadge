import sys
import logging
import random
from Signal.SignalClient import SignalClient
from Opaque.OpaqueClient import OpaqueClient
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal

logger = logging.getLogger("Client")

HOST = "localhost"
OPAQUE_PORT = 50051
SIGNAL_PORT = 50052
CERTIFILE_FILE = './localhost.crt'

class ChatApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.opaqueClient = OpaqueClient(HOST, OPAQUE_PORT, CERTIFILE_FILE)
        self.signalClient = SignalClient(12345, HOST, SIGNAL_PORT, CERTIFILE_FILE)
        self.login_widget = LoginWidget(self.opaqueClient, self.signalClient)
        self.search_ui = ChatSearchUI(self.opaqueClient, self.signalClient)
    
        # connect login signal to slot that changes widget displayed
        self.login_widget.login_signal.connect(self.show_search_ui)
        self.login_widget.show()

    def show_search_ui(self):
        self.login_widget.hide()
        self.search_ui.show()

class LoginWidget(QWidget):
    login_signal = pyqtSignal()

    def __init__(self, opaqueClient, signalClient):
        super().__init__()
        self.initUI()
        self.opaqueClient = opaqueClient
        self.signalClient = signalClient

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

        if username == "" or password == "":
            self.popupDialog("Error", "Please enter the Username and Password.", QMessageBox.Warning)
            return

        token = self.opaqueClient.login(username, password)
        if token != "":
            logger.info("Loggged in")
            self.signalClient.token = token
            self.signalClient.client_id = username
            self.login_signal.emit() # emit the login signal
        else:
            self.popupDialog("Error", "Invalid username or password.", QMessageBox.Warning)

    def register(self):
        username = self.username.text()
        password = self.password.text()

        if username == "" or password == "":
            self.popupDialog("Error", "Please enter the Username and Password.", QMessageBox.Warning)
            return

        registered = self.opaqueClient.register_user(username, password)
        if registered:
            logger.info("Successfully registered")
            self.popupDialog("Success", "User registered successfully!", QMessageBox.Information)
        else:
            self.popupDialog("Failure", "User already exists", QMessageBox.Information)
        
    def popupDialog(self, title, text, messageType):
        error_dialog = QMessageBox()
        error_dialog.setIcon(messageType)
        error_dialog.setText(text)
        error_dialog.setWindowTitle(title)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()

class ChatSearchUI(QWidget):
    def __init__(self, opaqueClient, signalClient):
        super().__init__()
        self.initUI()
        self.opaqueClient = opaqueClient
        self.signalClient = signalClient

    def initUI(self):
        self.setWindowTitle('Chat Messager')
        self.setGeometry(100, 100, 600, 500)

        # create header label
        header = QLabel('Crypto Messadge Search Chat')
        header.setStyleSheet('font-size: 20pt; font-weight: bold;')

        # Create widgets
        self.search_label = QLabel('Search Chat:')
        self.message_input = QLineEdit()
        self.search_button = QPushButton('Search')

        # Create layouts
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.search_label)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.search_button)
        input_layout.setContentsMargins(50, 50, 50, 150)

        main_layout = QVBoxLayout()
        main_layout.addWidget(header)
        main_layout.addLayout(input_layout)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Set layout
        self.setLayout(main_layout)

        # Connect signals and slots
        self.search_button.clicked.connect(self.search_message)

    def search_message(self):
        message = self.message_input.text()
        if message:
            self.message_input.clear()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = ChatApplication(sys.argv)
    sys.exit(app.exec_())