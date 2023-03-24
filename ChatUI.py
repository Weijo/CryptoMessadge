import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import json
from os.path import exists
import Util.messageStorage
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from Signal.SignalClient import SignalClient


class MessageListener(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, signalClient):
        super().__init__()
        self.signalClient = signalClient

    def run(self):
        for message in self.signalClient.heard():
            self.message_received.emit(message)

class ChatMessagingUI(QWidget):
    def __init__(self, signalClient, username, recipient_id):
        super().__init__()
        self.signalClient = signalClient
        self.username = username
        self.recipient_id = recipient_id
        self.MESSAGE_FILEPATH = self.username + "_messages.json"

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

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     chat_ui = ChatMessagingUI()
    
#     chat_ui.receive_message()
#     chat_ui.show()

#     sys.exit(app.exec_())
