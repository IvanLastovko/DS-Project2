import socket
import threading
import os

generals = []


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
            pass


def list_generals(generals):
    for general in generals:
        print(f"G{general.id}, {'primary' if general.is_primary else 'secondary'}, state={general.state}")


def execute_command(input_command, generals):
    cmd = input_command.lower().split()
    if cmd is None or len(cmd) == 0:
        print("Command is missing")
        return True

    command = cmd[0]

    if command == 'g-state':
        try:
            list_generals(generals)
        except:
            print("Error")

    elif command == 'exit':
        return False

    else:
        print("Command not found")

    return True

if __name__ == "__main__":
    N = 4
    for i in range(N):
        general = General(i + 1, 8000 + i, i == 0)
        generals.append(general)
        general.start()

    running = True
    while running:
        command = input("Command: ")
        running = execute_command(command, generals)

    # kill
    os._exit(0)
