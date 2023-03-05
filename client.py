import opaqueClient

ADDRESS = ("localhost", 8888)

def Connect2Server():
    client = opaqueClient.opaqueClient(ADDRESS)
    username = "bob"
    password = "password"

    client.register(username, password)
    client.login(username, password)

    resp = client.sendMessage(b"hello")
    print(resp)
    resp = client.sendMessage(b"noice")
    print(resp)

    client.close()

if __name__ == "__main__":
    Connect2Server()
