from client import Client

# init alice client
alice = Client('alice', '54321', 'localhost', 50051)
alice.subscribe()
alice.register_keys(1, 1)
message = input("Start message to bob: \n")
alice.publish(message, 'bob')

while True:
    message = input("")
    alice.publish(message, 'bob')