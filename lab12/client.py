import socket
import struct
import time
import os
import tkinter as tk
from tkinter import ttk

PACKET_SIZE = 4096

def tcp(host, port, num_packets):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.settimeout(10.0)
        bytes_sent = 0

        for i in range(num_packets):
            data = os.urandom(PACKET_SIZE-20)
            send_ts = time.time()
            header = struct.pack('!IdII', i, send_ts, len(data), num_packets)
            sock.sendall(header + data)

            bytes_sent += len(header) + len(data)

        end_ts = time.time()
        end_header = struct.pack('!IdII', num_packets, end_ts, 0, num_packets)
        sock.sendall(end_header)

    except Exception as e:
        print("TCP Error")
    finally:
        sock.close()
    return None


def udp(host, port, num_packets):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10.0)
        bytes_sent = 0

        for i in range(num_packets):
            data = os.urandom(PACKET_SIZE-20)
            send_ts = time.time()

            header = struct.pack('!IdII', i, send_ts, len(data), num_packets)
            sock.sendto(header + data, (host, port))
            bytes_sent += len(header) + len(data)
    except Exception as e:
        print("UDP Error")
    finally:
        sock.close()
    return None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client")
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

        ttk.Label(frame, text="Number:").grid(row=2, column=0, sticky="w", **pad)
        self.number_var = tk.StringVar()
        self.number_entry = ttk.Entry(frame, textvariable=self.number_var, width=22)
        self.number_entry.grid(row=2, column=1, sticky="ew", **pad)

        self.btn1 = ttk.Button(frame, text="run tcp", command=self._run_tcp)
        self.btn1.grid(row=3, column=0, **pad)

        self.btn2 = ttk.Button(frame, text="run udp", command=self._run_udp)
        self.btn2.grid(row=3, column=1, **pad)

    def _run_tcp(self):
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        number = self.number_var.get().strip()
        tcp(ip, int(port), int(number))

    def _run_udp(self):
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        number = self.number_var.get().strip()
        udp(ip, int(port), int(number))



if __name__ == "__main__":
    app = App()
    app.mainloop()