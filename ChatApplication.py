import sys
import logging
import Util.messageStorage
from Signal.SignalClient import SignalClient
from Opaque.OpaqueClient import OpaqueClient
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSignal, QThread

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
        self.chat_ui = None


        # connect login signal to slot that changes widget displayed
        self.login_widget.login_signal.connect(self.show_search_ui)
        self.login_widget.show()

        # connect search signal
        self.search_ui.search_signal.connect(self.show_message_ui)

    def show_search_ui(self):
        self.login_widget.hide()
        self.search_ui.show()

    def show_message_ui(self, recipient_id):
        self.chat_ui = ChatMessagingUI(self.signalClient, self.signalClient.client_id, recipient_id=recipient_id)
        self.chat_ui.show()
        self.search_ui.hide()

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
            self.signalClient.dbpath = username+"_Store.db"

            self.signalClient.subscribe()

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

            # Register keys
            self.signalClient.client_id = username
            self.signalClient.dbpath = username+"_Store.db"
            self.signalClient.register_keys(1)

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
    search_signal = pyqtSignal(str)

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
        recipient_id = self.message_input.text()
        if recipient_id:
            if recipient_id == self.signalClient.client_id:
                self.popupDialog("Failure", "That's you man", QMessageBox.Information)
                return

            print(self.message_input)
            response_receiver_key = self.signalClient.GetReceiverKey(recipient_id, False)

            if response_receiver_key is not None:
                self.signalClient.recipient_id = recipient_id
                self.search_signal.emit(recipient_id)
            else:
                self.popupDialog("Failure", "User not found", QMessageBox.Information)

            self.message_input.clear()
    
    def popupDialog(self, title, text, messageType):
        error_dialog = QMessageBox()
        error_dialog.setIcon(messageType)
        error_dialog.setText(text)
        error_dialog.setWindowTitle(title)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()
            
class MessageListener(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, signalClient):
        super().__init__()
        self.signalClient = signalClient

    def run(self):
        for message in self.signalClient.heard():
            self.message_received.emit(message)

class ChatMessagingUI(QWidget):
    def __init__(self, signalClient, username="", recipient_id=""):
        super().__init__()
        self.signalClient = signalClient
        self.username = self.signalClient.client_id
        self.recipient_id = self.signalClient.recipient_id

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.recipient_id)
        self.setGeometry(100, 100, 600, 500)

        # Create widgets
        self.history_list = QListWidget()
        self.message_input = QLineEdit()
        self.send_button = QPushButton('Send')
        self.clear_button = QPushButton('Clear')

        # Create layouts
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.history_list)
        main_layout.addLayout(input_layout)

        # Set layout
        self.setLayout(main_layout)

        # Connect signals and slots
        self.send_button.clicked.connect(self.send_message)
        self.clear_button.clicked.connect(self.clear_history)

        # Start message listener thread
        self.message_listener = MessageListener(self.signalClient)
        self.message_listener_thread = QThread()
        self.message_listener.moveToThread(self.message_listener_thread)
        self.message_listener.message_received.connect(self.update_messages)
        self.message_listener_thread.started.connect(self.message_listener.run)
        self.message_listener_thread.start()

        # populate data
        # Define password and salt
        password = b"1ct2205?!"
        salt = b"verysaltytears"

        # Derive the decryption key and create an instance of the Fernet class
        key = Util.messageStorage.get_encryption_key(password, salt)
        cipher_suite = Util.messageStorage.create_cipher_suite(key)

        # connect to database.
        conn = Util.messageStorage.connect_to_database(self.username)
        cursor = conn.execute("SELECT sender, recipient, encrypted_message FROM messages WHERE convo_id=? OR convo_id=?",
                              (self.username + "-" + self.recipient_id, self.recipient_id + "-" + self.username,))

        all_relevant_entries = cursor.fetchall()
        print("all_relevant_entries: ", all_relevant_entries)

        for relevant_entry in all_relevant_entries:
            sender = relevant_entry[0]
            recipient = relevant_entry[1]
            encrypted_message = relevant_entry[2]

            decrypted_message = Util.messageStorage.decrypt_body(cipher_suite, encrypted_message).decode()

            if sender == self.recipient_id:
                item = QListWidgetItem(self.recipient_id + ": " + decrypted_message)
            elif sender == self.username:
                item = QListWidgetItem("You: " + decrypted_message)

            self.history_list.addItem(item)

        # Close the database connection
        Util.messageStorage.close_database(conn)

        self.message_input.clear()

    def send_message(self):
        message = self.message_input.text()

        self.signalClient.publish(message, self.recipient_id)

        if message:
            item = QListWidgetItem("You: " + message)
            self.history_list.addItem(item)
            self.message_input.clear()

    def clear_history(self):
        self.history_list.clear()

    def update_messages(self, message):
        if message:
            item = QListWidgetItem("{}: {}".format(self.recipient_id, message))
            self.history_list.addItem(item)
            self.message_input.clear()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = ChatApplication(sys.argv)
    sys.exit(app.exec_())