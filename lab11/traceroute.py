import socket
import sys
import random
import struct
import time


def get_checksum(data):
        summa = 0
        count = 0
        while count < (len(data) // 2) * 2:
            summa += data[count + 1] * 256 + data[count]
            summa &= 0xffffffff
            count += 2
        if len(data)%2 != 0:
            summa += data[len(data) - 1]
            summa &= 0xffffffff

        summa = (summa >> 16) + (summa & 0xffff)
        summa += (summa >> 16)
        answer = ~summa & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer


def create_icmp_packet(identifier, sequence):
    packet = struct.pack('!BBHHH', 8, 0, 0, identifier, sequence)
    data = b'\x00' * 64
    packet += data
    checksum = get_checksum(packet)
    packet = struct.pack('!BBHHH', 8, 0, checksum, identifier, sequence) + data
    return packet


def create_raw_socket(ttl, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.settimeout(timeout)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    return sock


def receive_reply(sock, identifier, sequence, timeout, start_time):
    while (time.time() - start_time) < timeout:
        try:
            recv_packet, addr = sock.recvfrom(1024)
            recv_time = time.time()
            rtt = (recv_time - start_time) * 1000
            ip_header = recv_packet[:20]
            ip_header_len = (ip_header[0] & 0x0F) * 4
            icmp_packet = recv_packet[ip_header_len:]
            icmp_type, icmp_code, checksum, recv_id, recv_seq = struct.unpack('!BBHHH', icmp_packet[:8])
            if icmp_type == 0 and recv_id == identifier and recv_seq == sequence:
                return addr[0], rtt
            elif icmp_type == 11:
                original_icmp = icmp_packet[28:36]
                orig_type, orig_code, orig_checksum, orig_id, orig_seq = struct.unpack('!BBHHH', original_icmp[:8])
                if orig_id == identifier and orig_seq == sequence:
                    return addr[0], rtt
        except socket.timeout:
            return None, None
    return None, None


def trace(host, max_hops, timeout, num_messages):
    identifier = random.randint(1, 0xFFFF)
    sequence = 0
    for ttl in range(1, max_hops + 1):
        hop_address = None
        rtts = []
        for i in range(num_messages):
            sock = create_raw_socket(ttl, timeout)
            packet = create_icmp_packet(identifier, sequence)
            try:
                send_time = time.time()
                sock.sendto(packet, (host, 0))
                address, rtt = receive_reply(sock, identifier, sequence, timeout, send_time)
                if address:
                    hop_address = address
                    rtts.append(round(rtt, 3))
                else:
                    rtts.append(-1)

            except socket.error as e:
                rtts.append(-1)
            finally:
                sock.close()
            sequence += 1
        if hop_address:
            try:
                hostname = socket.gethostbyaddr(hop_address)[0]
            except:
                hostname = ""
            line = ""
            for rtt in rtts:
                if rtt == -1:
                    line += "    *    "
                else:
                    line += "   "+str(rtt)+"   "

            print(ttl, line, hop_address, hostname)
            if hop_address == host:
                print("Destination reached at hop "+str(ttl))
                break
        else:
            print(ttl, "Request timeout")
    print("Traceroute complete")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Incorrect format")
    else:
        host_ip = sys.argv[1]
        max_hops = 30
        timeout = 5
        num_messages = int(sys.argv[2])
        trace(host_ip, max_hops, timeout, num_messages)
