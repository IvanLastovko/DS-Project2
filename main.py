import socket
import threading


class General(threading.Thread):

    def __init__(self, id, port, is_primary):
        super(General, self).__init__(daemon=False)

        self.id = id
        self.host = '127.0.0.1'
        self.port = port

        self.state = 'NF'
        self.received_orders = {}
        self.decision = None
        self.is_primary = is_primary

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

    def init_server(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1)
        self.sock.listen()

    def run(self):
        while True:
            print(1)
            break


if __name__ == "__main__":
    N = 4
    generals = []
    for i in range(N):
        general = General(i + 1, 8000 + i, i == 0)
        generals.append(general)
        general.start()
