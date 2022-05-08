import socket
import threading
import os
import random
import time
import sys

generals = []


class General(threading.Thread):

    def __init__(self, id, port, is_primary):
        super(General, self).__init__(daemon=False)

        self.id = id
        self.host = '127.0.0.1'
        self.port = port

        self.state = 'NF'
        self.node_ports = {}
        self.decision = None
        self.is_primary = is_primary
        self.primary_message = None
        self.received_messages = 0
        self.majority = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

    def set_state(self, state):
        if state.lower() == 'faulty':
            self.state = 'F'
        elif state.lower() == 'non-faulty':
            self.state = 'NF'

    def collect_node_port(self, port):
        self.node_ports[port] = None

    def send_request(self, port, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, port))
        sock.send((str(message) + '|' + str(self.port)).encode('utf-8'))

    def action(self, message):
        message, port = message.split('|')
        if int(port) not in self.node_ports:
            self.primary_message = message
            self.send_everyone(message, self.state == 'F')
        else:
            self.node_ports[int(port)] = message
            self.received_messages += 1
            if self.received_messages == len(self.node_ports):
                self.received_messages = 0
                self.count_majority()

    def count_majority(self):
        answers = {'attack': 0, 'retreat': 0}
        for port in self.node_ports:
            answers[self.node_ports[port]] += 1
        answers[self.primary_message] += 1

        if answers['attack'] != answers['retreat']:
            self.majority = 'attack' if answers['attack'] > answers['retreat'] else 'retreat'
        else:
            self.majority = 'undefined'

    def get_request(self):
        try:
            connection, client_address = self.sock.accept()
            message = connection.recv(4096).decode('utf-8')
            self.action(message)
        except:
            pass

    def init_server(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1)
        self.sock.listen()

    def send_everyone(self, message, is_faulty):
        for port in self.node_ports.keys():
            self.send_request(port, random.choice(['attack', 'retreat']) if is_faulty else message)

    def run(self):
        while True:
            self.get_request()


def list_generals(generals, print_primary=True, print_state=True, print_majority=False):
    for general in generals:
        print(f"G{general.id}"
              f"{(', primary' if general.is_primary else ', secondary') if print_primary else ''}"
              f"{(', majority=' + general.majority) if print_majority else ''}"
              f"{(', state=' + general.state) if print_state else ''}")


def set_state(id, state, generals):
    for gen in generals:
        if gen.id == int(id):
            gen.set_state(state)
            break
    list_generals(generals, False, True, False)


def delete_node(id, generals):
    for index, gen in enumerate(generals):
        if gen.id == int(id):
            gen.sock.close()
            generals.pop(index)
            break
    generals[0].is_primary = True
    list_generals(generals, False, True)
    save_node_ports(generals)


def add_nodes(amount, generals):
    max_id = generals[-1].id
    for i in range(int(amount)):
        general = General(i + max_id + 1, 8000 + i + max_id, False)
        general.start()
        generals.append(general)
    save_node_ports(generals)
    list_generals(generals, True, False)


def call_coordinator(generals, order):
    faulty_generals = 0
    total_generals = len(generals)
    choices = {'attack': 0, 'retreat': 0, 'undefined': 0}

    for node in generals:
        faulty_generals += 1 if node.state == 'F' and not node.is_primary else 0
        if not node.is_primary:
            choices[node.majority] += 1

    majority = 'attack' if choices['attack'] > choices['retreat'] else 'retreat'

    if faulty_generals * 3 + 1 > total_generals:
        for node in generals:
            if not node.is_primary:
                node.majority = 'undefined'
        list_generals(generals, False, True, True)
        print('Execute order: cannot be determined – not enough generals in the system! '
              f'{faulty_generals} faulty node in the system - {total_generals - 1} out of {total_generals} quorum not consistent')
    else:
        list_generals(generals, False, True, True)
        print(
            f'Execute order: {majority}! {str(faulty_generals) + " faulty" if faulty_generals else "Non-faulty"} '
            f'node{"s" if faulty_generals > 1 else ""} in the system – '
            f'{total_generals - 1 - faulty_generals} out of {total_generals} quorum suggest {majority}')


def send_order(order, generals):
    if generals[0].is_primary:
        generals[0].majority = order
        generals[0].send_everyone(order, generals[0].state == 'F')
    else:
        print("Error! General is not primary!")

    found_none = True
    while found_none:
        found_none = False
        for node in generals:
            if node.majority is None:
                found_none = True

    call_coordinator(generals, order)
    save_node_ports(generals)


def save_node_ports(generals):
    for node_host in generals:
        node_host.node_ports = {}
        node_host.majority = None
        for node_client in generals:
            if node_host.id != node_client.id and not node_client.is_primary:
                node_host.collect_node_port(node_client.port)


def execute_command(input_command, generals):
    cmd = input_command.lower().split()
    if cmd is None or len(cmd) == 0:
        print("Command is missing")
        return True

    command = cmd[0]

    if len(cmd) == 1 and command == 'g-state':
        try:
            list_generals(generals)
        except:
            print("Error")

    elif len(cmd) == 3 and command == 'g-state':
        try:
            set_state(cmd[1], cmd[2], generals)
        except:
            print("Error")

    elif command == 'g-kill':
        try:
            delete_node(cmd[1], generals)
        except:
            print("Error")

    elif command == 'g-add':
        try:
            add_nodes(cmd[1], generals)
        except:
            print("Error")

    elif command == 'actual-order':
        try:
            send_order(cmd[1], generals)
        except:
            print("Error")

    elif command == 'exit':
        return False

    else:
        print("Command not found")

    return True


if __name__ == "__main__":
    N = int(sys.argv[1])
    if N == 0:
        print("Can not create 0 generals")
        os._exit(0)

    for i in range(N):
        general = General(i + 1, 8000 + i, i == 0)
        general.start()
        generals.append(general)

    save_node_ports(generals)

    running = True
    while running:
        command = input("Command: ")
        running = execute_command(command, generals)

    # kill
    os._exit(0)
