import socket
import os
import threading

# Caminho correto para conteudo_server2/files
BASE_DIR = os.path.join(os.path.dirname(__file__), "files")

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 7001))
    s.listen(5)
    print("[S2 TCP] Servidor TCP rodando em 0.0.0.0:7001")

    while True:
        conn, addr = s.accept()
        print(f"[S2 TCP] Conexão de {addr}")

        # Recebe o nome do arquivo
        raw = conn.recv(1024)

        if not raw:
            print("[S2 TCP] ERRO: Cliente enviou requisição vazia.")
            conn.send(b"NOT_FOUND".ljust(16, b' '))
            conn.close()
            continue

        filename = raw.decode().strip()
        filepath = os.path.join(BASE_DIR, filename)

        # Caso filename esteja vazio
        if filename == "":
            print("[S2 TCP] ERRO: Nome de arquivo vazio recebido.")
            conn.send(b"NOT_FOUND".ljust(16, b' '))
            conn.close()
            continue

        # Verifica se o arquivo existe
        if not os.path.isfile(filepath):
            print(f"[S2 TCP] Arquivo NÃO encontrado: {filename}")
            conn.send(b"NOT_FOUND".ljust(16, b' '))
            conn.close()
            continue

        # Envia tamanho do arquivo
        filesize = os.path.getsize(filepath)
        conn.send(str(filesize).encode().ljust(16, b' '))

        # Envia o arquivo real
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                conn.sendall(chunk)

        print(f"[S2 TCP] Arquivo enviado: {filename} ({filesize} bytes)")
        conn.close()


# Mantém servidor ativo
tcp_server()
