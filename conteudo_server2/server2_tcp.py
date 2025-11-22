import socket
import os
import threading

BASE_PATH = "./conteudo_server2/files/"

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7001))
    s.listen(5)
    print("S2 TCP pronto")

    while True:
        conn, addr = s.accept()
        filename = conn.recv(1024).decode().strip()
        path = BASE_PATH + filename

        if not os.path.exists(path):
            conn.send(b"NOT_FOUND")
            conn.close()
            continue

        with open(path, "rb") as f:
            data = f.read()

        conn.sendall(data)
        conn.close()

def udp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", 7002))
    print("S2 UDP pronto")

    while True:
        data, addr = s.recvfrom(4096)
        filename = data.decode().strip()
        path = BASE_PATH + filename

        if not os.path.exists(path):
            s.sendto(b"NOT_FOUND", addr)
            continue

        with open(path, "rb") as f:
            udp_data = f.read()

        s.sendto(udp_data, addr)

threading.Thread(target=tcp_server).start()
threading.Thread(target=udp_server).start()
