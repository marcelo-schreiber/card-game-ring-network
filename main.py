import socket
from time import sleep

class Node:
    def __init__(self, address, next_address, has_token=False):
        self.address = address
        self.next_address = next_address
        self.has_token = has_token

        # socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)

        if self.has_token:
            self.send_data()

    def send_data(self):
        if not self.has_token and not frame:
            return            

        port_from = self.address[1]
        port_to_send_to = input("Enter the port to send to: ")
        message = input("Enter the message to send: ")
        ack = "0"
        frame = f"{port_from}:{port_to_send_to}:{message}:{ack}"

        self.sock.sendto(frame.encode(), self.next_address)

    def send_token(self):
        self.has_token = False
        self.sock.sendto("TOKEN".encode(), self.next_address)

    def listen(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            data = data.decode()
            
            print("-="*5, "Listened", "-="*5)
            print(data)
            print("-="*18)

            if data == "TOKEN": # if received a token
                self.has_token = True
                self.send_data() # I can send data
            else: # if received a data frame
                msg_address, port_to_send_to, message, ack = data.split(":")

                try :
                    int(msg_address)
                    int(port_to_send_to)
                except ValueError:
                    print("Found an invalid frame, skipping")
                    continue

                if int(port_to_send_to) == self.address[1]: # If the message is for me
                    print(f"I received a message: {message}")
                    ack = "1"
                    frame = f"{msg_address}:{port_to_send_to}:{message}:{ack}"
                    self.sock.sendto(frame.encode(), self.next_address)
                elif int(msg_address) == self.address[1]: # If the message is from me
                    if ack == "1":
                        print(f"Found an ACK for the message I sent, sending token")
                        self.send_token() # TODO: some timeout mechanism, a node can send multiple times
                else:
                    self.sock.sendto(data.encode(), self.next_address)

if __name__ == "__main__":
    from_ip = input("Enter the IP address of this node: ")
    port = int(input("Enter the port number of this node: "))

    ip = input("Enter the IP address of the next node: ")
    next_port = int(input("Enter the next port number of the next node: "))

    if from_ip == "":
        from_ip = socket.gethostbyname(socket.gethostname())
    
    has_token  = input("Do you have the token? (y/n): ") 

    if has_token == "y":
        has_token = True
    else:
        has_token = False
    
    node = Node((from_ip, port), (ip, next_port), has_token)
    node.listen()

    
