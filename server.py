import socketserver
import signal
import opaqueServer

ADDRESS = ("127.0.0.1", 8888)

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGPIPE, signal.SIG_DFL)


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Receive data from the client
        data = self.request.recv(1024).strip()

        # Extract the request type and data from the received data
        request_type = data[0]
        request_data = data[1:]

        # Handle the different types of requests
        if request_type == 1:
            # Type 1 request: register
            opaqueHandler.handle_registration(self.request, request_data)

        elif request_type == 2:
            # Type 2 request: login
            if opaqueHandler.handle_login(self.request, request_data):
                # Continuously receive and process messages from client
                while True:
                    # Receive encrypted message from client
                    encrypted_data = self.request.recv(1024)
                    if not encrypted_data:
                        # Connection closed by client, exit loop
                        break

                    data = opaqueHandler.decrypt(encrypted_data)
                    print(f"Received data: {data}")
                    # For now send back the data
                    encrypted_response = opaqueHandler.encrypt(data)
                    self.request.sendall(encrypted_response.encode())

        # For now, just put the signal stuff here.
        elif request_type == 3:
            # Type 3 request: Signal
            pass

        else:
            # Unknown request type: send an error message back to the client
            response_data = b"Error: unknown request type"
            self.request.sendall(response_data)


if __name__ == "__main__":
    opaqueHandler = opaqueServer.opaqueServer()

    with socketserver.ThreadingTCPServer(ADDRESS, MyTCPHandler) as server:
        server.serve_forever()
