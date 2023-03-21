import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import json
from os.path import exists
from PyQt5.QtCore import QObject, pyqtSignal, QThread

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
        # Replace TESINT with populated data from database
        item = QListWidgetItem("TESINT")
        self.history_list.addItem(item)
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
