import sys
from PyQt5.QtWidgets import *

class ChatSearchUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

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
    app = QApplication(sys.argv)
    search_ui = ChatSearchUI()
    search_ui.show()
    sys.exit(app.exec_())
