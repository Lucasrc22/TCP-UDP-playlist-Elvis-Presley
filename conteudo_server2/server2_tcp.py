import socket
import os
import threading

# Use a path relative to this script
BASE_DIR = os.path.join(os.path.dirname(__file__), "files")

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7001))
    s.listen(5)
    print("S2 TCP pronto")

    while True:
        conn, addr = s.accept()
        filename = conn.recv(1024).decode().strip()
        filepath = os.path.join(BASE_DIR, filename)

        if not os.path.exists(filepath):
            conn.send(b"NOT_FOUND")
            conn.close()
            continue

        # Envia primeiro o tamanho do arquivo (16 bytes), compatível com o cliente
        filesize = os.path.getsize(filepath)
        conn.send(f"{filesize}".encode().ljust(16, b' '))

        # Envia o arquivo em blocos
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                conn.sendall(chunk)

        conn.close()

def udp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", 7002))
    print("S2 UDP pronto")

    while True:
        data, addr = s.recvfrom(4096)
        filename = data.decode().strip()
        filepath = os.path.join(BASE_DIR, filename)

        if not os.path.exists(filepath):
            s.sendto(b"NOT_FOUND", addr)
            continue

        with open(filepath, "rb") as f:
            udp_data = f.read()

        s.sendto(udp_data, addr)

threading.Thread(target=tcp_server).start()
threading.Thread(target=udp_server).start()
