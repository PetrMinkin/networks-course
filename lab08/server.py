import random
from socket import socket, AF_INET, SOCK_DGRAM
from checksum import check_checksum
PORT = 20039
L = 4096

if __name__ == "__main__":

    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('localhost', PORT))
    data = b''
    number = 0

    while True:
        packet, client = server_socket.recvfrom(L)
        if random.random() < 0.3:
            print("Packet got lost")
            continue

        packet_number = packet[0]
        is_last = packet[1]
        checksum = int.from_bytes(packet[2:4], 'big')
        received_data = packet[4:]
        print("Received a packet")
        ack = bytes([packet_number])

        if not check_checksum(received_data, checksum):
            print("Wrong checksum")
            continue

        if packet_number != number:
            print("Wrong packet")
            server_socket.sendto(ack, client)
            continue

        data += received_data
        number = 1 - number
        server_socket.sendto(ack, client)
        if is_last:
            print("Received the file")
            break


    with open("images/image.png", "wb") as f:
        f.write(data)
