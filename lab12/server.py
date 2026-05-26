import socket
import struct
import time
import tkinter as tk
from tkinter import ttk

PACKET_SIZE = 4096


def measure_speed(received, duration):
    return received * 8 / (duration * 1_000_000)


def tcp(ip, port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((ip, port))
    srv.listen(5)
    srv.settimeout(1.0)
    while True:
        try:
            conn, addr = srv.accept()
            break
        except socket.timeout:
            continue
    bytes_received = 0
    start_time = None
    total = None
    received = 0
    try:
        while True:
            packet = conn.recv(PACKET_SIZE)
            header = packet[:20]
            seq_num, send_ts, data_len, total_pkts = struct.unpack('!IdII', header)
            if start_time is None:
                start_time = send_ts
                total = total_pkts
            bytes_received += data_len
            if data_len == 0:
                break
            else:
                received += 1

    except Exception as e:
        print("TCP error")
    finally:
        end_time = time.time()
        conn.close()
        srv.close()
        return round(measure_speed(bytes_received, end_time - start_time), 3), str(received) + " out of " + str(total)



def udp(ip, port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((ip, port))
    srv.settimeout(1.0)
    received = set()
    bytes_received = 0
    timeout = 60
    start_time = None
    total = None
    start_server = time.time()
    while True:
        try:
            packet, addr = srv.recvfrom(PACKET_SIZE)
            header = packet[:20]
            seq_num, send_ts,  data_len, total_pkts = struct.unpack('!IdII', header)
            if start_time is None:
                start_time = send_ts
                total = total_pkts
            received.add(seq_num)
            bytes_received += data_len
            if len(received) == total_pkts:
                break
        except socket.timeout:
            continue
        if time.time() - start_server > timeout:
            break
    end_time = time.time()
    srv.close()
    return round(measure_speed(bytes_received, end_time - start_time), 3), str(len(received)) +" out of "+str(total)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Server")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="IP Address:").grid(row=0, column=0, sticky="w", **pad)
        self.ip_var = tk.StringVar()
        self.ip_entry = ttk.Entry(frame, textvariable=self.ip_var, width=22)
        self.ip_entry.grid(row=0, column=1, sticky="ew", **pad)

        ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky="w", **pad)
        self.port_var = tk.StringVar()
        self.port_entry = ttk.Entry(frame, textvariable=self.port_var, width=22)
        self.port_entry.grid(row=1, column=1, sticky="ew", **pad)

        ttk.Label(frame, text="Speed (Mbps):").grid(row=3, column=0, sticky="w", **pad)
        self.out1_var = tk.StringVar(value="—")
        out1 = ttk.Entry(frame, textvariable=self.out1_var, width=26, state="readonly")
        out1.grid(row=3, column=1, sticky="ew", **pad)

        ttk.Label(frame, text="Received:").grid(row=4, column=0, sticky="w", **pad)
        self.out2_var = tk.StringVar(value="—")
        out2 = ttk.Entry(frame, textvariable=self.out2_var, width=26, state="readonly")
        out2.grid(row=4, column=1, sticky="ew", **pad)

        self.btn1 = ttk.Button(frame, text="run tcp", command=self._run_tcp)
        self.btn1.grid(row=5, column=0, **pad)

        self.btn2 = ttk.Button(frame, text="run udp", command=self._run_udp)
        self.btn2.grid(row=5, column=1, **pad)

    def _run_tcp(self):
        ip = self.ip_var.get().strip()
        port = int(self.port_var.get().strip())
        speed, num = tcp(ip, port)
        self.out1_var.set(speed)
        self.out2_var.set(num)

    def _run_udp(self):
        ip = self.ip_var.get().strip()
        port = int(self.port_var.get().strip())
        speed, num = udp(ip, port)
        self.out1_var.set(speed)
        self.out2_var.set(num)

if __name__ == "__main__":
    app = App()
    app.mainloop()