import OpaqueClient

if __name__ == "__main__":
    client = OpaqueClient.OpaqueClient("127.0.0.1", "50051")

    # Test register
    registered = client.register_user("alice", "password123")
    print(f"{registered=}")
    
    registered = client.register_user("alice", "asd")
    print(f"{registered=}")
    

    # Test login
    token = client.login("alice", "password123")
    if token != "":
        print(f"{token=}")

    token = client.login("alice", "asd")