import socket
import os

UDP_IP = "0.0.0.0"
UDP_PORT = 7002
# Use a path relative to this script
BASE_DIR = os.path.join(os.path.dirname(__file__), "files")


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"[SERVER2-UDP] Servidor UDP rodando na porta {UDP_PORT}...")

while True:
    try:
        data, addr = sock.recvfrom(1024)
        filename = data.decode().strip()
        print(f"[SERVER2-UDP] Pedido de {addr}: {filename}")

        filepath = os.path.join(BASE_DIR, filename)

        if not os.path.exists(filepath):
            print("[SERVER2-UDP] Arquivo não encontrado.")
            sock.sendto(b"NOT_FOUND", addr)
            continue

        with open(filepath, "rb") as f:
            chunk = f.read(4096)
            while chunk:
                sock.sendto(chunk, addr)
                chunk = f.read(4096)

        sock.sendto(b"<<FIN>>", addr)

        print(f"[SERVER2-UDP] Arquivo {filename} enviado com sucesso!")

    except KeyboardInterrupt:
        print("\n[SERVER2-UDP] Encerrando servidor UDP.")
        break

sock.close()
