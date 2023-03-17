import sys
#from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import *

class ChatMessagingUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Chat Messager')
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

    def send_message(self):
        message = self.message_input.text()
        if message:
            item = QListWidgetItem(message)
            self.history_list.addItem(item)
            self.message_input.clear()

    def clear_history(self):
        self.history_list.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_ui = ChatMessagingUI()
    chat_ui.show()
    sys.exit(app.exec_())
