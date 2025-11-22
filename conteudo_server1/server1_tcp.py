import socket
import os

BASE_PATH = "/home/guest/Documentos/Redes/Redes2/conteudo_server1/files/"

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 6001))
    s.listen(5)
    print("TCP Server pronto na porta 6001")

    while True:
        conn, addr = s.accept()
        print("Cliente conectado:", addr)

        # Recebe o nome do arquivo
        filename = conn.recv(1024).decode().strip()
        filepath = BASE_PATH + filename

        if not os.path.exists(filepath):
            print("Arquivo não encontrado:", filename)
            conn.send(b"NOT_FOUND")
            conn.close()
            continue

        # Envia primeiro o tamanho do arquivo (8 bytes)
        filesize = os.path.getsize(filepath)
        conn.send(f"{filesize}".encode().ljust(16, b' '))

        print(f"Enviando {filename} ({filesize} bytes)...")

        # Envia o arquivo em blocos
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                conn.sendall(chunk)

        print("Envio concluído.\n")
        conn.close()


if __name__ == "__main__":
    tcp_server()
