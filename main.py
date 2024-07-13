import socket
import threading
import time

class Node:
    def __init__(self, address, next_address, has_token=False):
        self.address = address
        self.next_address = next_address
        self.has_token = has_token

        # socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)

    def send_data(self, frame = None):
        if not self.has_token and not frame:
            return

        if not self.has_token and frame:
            self.sock.sendto(frame.encode(), self.next_address)

        port_to_send_to = input("Enter the port to send to: ")
        message = input("Enter the message to send: ")
        ack = "0"
        frame = f"{self.address[1]}:{port_to_send_to}:{message}:{ack}"

        self.sock.sendto(frame.encode(), self.next_address)

    def send_token(self):
        self.has_token = False
        self.sock.sendto("TOKEN".encode(), self.next_address)

    def listen(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            data = data.decode()

            if data == "TOKEN": # if received a token
                self.has_token = True
                print(f"Node {self.address[1]} has token")
                self.send_data() # I can send data
            else: # if received a data frame
                msg_address, port_to_send_to, message, ack = data.split(":")

                if int(port_to_send_to) == self.address[1]: # If the message is for me
                    print(f"Node {self.address[1]} received message: {message}")
                    ack = "1"
                    frame = f"{msg_address}:{port_to_send_to}:{message}:{ack}"
                    self.send_data(frame)
                elif msg_address == self.address[1]: # If the message is from me
                    if ack == "1":
                        self.send_token() # TODO: some timeout mechanism, a node can send multiple times
                    else:
                        self.send_data() # I can send data
                else:
                    self.send_data(data)

    def run(self):
        receive_thread = threading.Thread(target=self.listen)
        receive_thread.daemon = True
        receive_thread.start()
        receive_thread.join()
        # self.listen()

        while True:
            time.sleep(1)  # Keep the main thread alive

if __name__ == "__main__":
    # Define the addresses for each node in the network
    node1 = Node(('localhost', 10001), ('localhost', 10002))
    node2 = Node(('localhost', 10002), ('localhost', 10003))
    node3 = Node(('localhost', 10003), ('localhost', 10001))

    nodes = [node1, node2, node3]

    for node in nodes:
        threading.Thread(target=node.run).start()

    # send the token to the first node
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto("TOKEN".encode(), node1.address)

    while True:
        time.sleep(1)
