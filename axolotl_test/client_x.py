from client import Client

username = input("Enter your username: ")

x = Client(username, '54321', 'localhost', 50051)
x.subscribe()
x.register_keys(1, 1)

recipient_id = input("Enter a username to talk to: ")

response_receiver_key = x.GetReceiverKey(recipient_id)

if response_receiver_key is not None:
    message = input("Start message to {}: \n".format(recipient_id))
    x.publish(message, recipient_id)

    while True:
        message = input("")
        x.publish(message, recipient_id)
else:
    print("The username '{}' cannot be found.".format(recipient_id))
