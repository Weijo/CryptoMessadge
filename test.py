import logging
from Signal.SignalClient import SignalClient
from Opaque.OpaqueClient import OpaqueClient
import sys
from PyQt5.QtWidgets import *
import ChatUI as ChatUI

logger = logging.getLogger("Client")

HOST = "localhost"
OPAQUE_PORT = 50051
SIGNAL_PORT = 50052
CERTIFILE_FILE = './localhost.crt'

def main():
    logger.info("Poggurz")

    with OpaqueClient(HOST, OPAQUE_PORT, CERTIFILE_FILE) as opaqueClient:
        # Authentication
        while True:
            register = input("Choose method: \n1) Register\n2) Login\n")
            username = input("Enter username: ")
            password = input("Enter password: ")

            if register == "1":
                registered = opaqueClient.register_user(username, password)
                if registered:
                    logger.info("Successfully registered")
            elif register == "2":
                token = opaqueClient.login(username, password)
                if token != "":
                    break
            else:
                logger.warning("Invalid type choose 1 or 2")


        # Chatting
        with SignalClient(12345, HOST, SIGNAL_PORT, CERTIFILE_FILE, username, token) as signalClient:
            signalClient.subscribe()
            signalClient.register_keys(1, 1)

            recipient_id = input("Enter a username to talk to: ")
            response_receiver_key = signalClient.GetReceiverKey(recipient_id)

            if response_receiver_key is not None:
                while True:
                    app = QApplication(sys.argv)
                    chat_ui = ChatUI.ChatMessagingUI(signalClient, username, recipient_id)
                    chat_ui.show()
                    sys.exit(app.exec_())
            else:
                print("The username '{}' cannot be found.".format(recipient_id))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()