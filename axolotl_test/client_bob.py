from client import Client

bob = Client('bob', '54321', 'localhost', 50051)
bob.subscribe()
bob.register_keys(1, 1)
message = input("Start message to alice: \n")
bob.publish(message, 'alice')

while True:
    message = input("")
    bob.publish(message, 'alice')