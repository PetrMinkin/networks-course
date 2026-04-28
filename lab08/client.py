import random
from socket import socket, AF_INET, SOCK_DGRAM
import sys
from checksum import find_checksum

PORT = 20039
L = 4096

def split(filename):
    with open(filename, "rb") as f:
        data = f.read()
    chunk_size = L - 4
    packets = []
    packet_number = 1
    for i in range(0, len(data), chunk_size):
        right_end = min(i+chunk_size, len(data))
        chunk = data[i:right_end]
        packet_number = 1 - packet_number
        is_last = False
        if i+chunk_size >= len(data):
            is_last = True
        checksum = find_checksum(chunk)
        packets.append(bytes([packet_number]) + bytes([is_last]) + checksum.to_bytes(2, 'big') + chunk)
    return packets


if __name__ == "__main__":
    timeout = float(sys.argv[2])
    packets = split(sys.argv[1])
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.settimeout(timeout)

    server_address = ('localhost', PORT)
    for packet in packets:
        while True:
            print("Sending packet")
            client_socket.sendto(packet, server_address)
            try:
                ack, _ = client_socket.recvfrom(L)
                if ack[0] == packet[0]:
                    print("ACK received: ", ack[0])
                    break
                else:
                    print("Wrong ACK")
            except TimeoutError:
                print("Timeout Error")
