import socket
import os
import threading

# Caminho correto: o script está dentro de conteudo_server1/
BASE_DIR = os.path.join(os.path.dirname(__file__), "files")

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 6001))
    s.listen(5)
    print("[S1 TCP] Servidor TCP rodando em 0.0.0.0:6001")

    while True:
        conn, addr = s.accept()
        print(f"[S1 TCP] Conexão de {addr}")

        raw = conn.recv(1024)
        if not raw:
            print("[S1 TCP] Erro: cliente enviou vazio")
            conn.send(b"NOT_FOUND".ljust(16, b' '))
            conn.close()
            continue

        filename = raw.decode().strip()

        # TRAVA IMPORTANTE AQUI
        if filename == "" or filename == "." or filename == "/":
            print("[S1 TCP] Erro: nome de arquivo inválido")
            conn.send(b"NOT_FOUND".ljust(16, b' '))
            conn.close()
            continue

        filepath = os.path.join(BASE_DIR, filename)

        if not os.path.isfile(filepath):
            print(f"[S1 TCP] Arquivo NÃO encontrado: {filename}")
            conn.send(b"NOT_FOUND".ljust(16, b' '))
            conn.close()
            continue

        filesize = os.path.getsize(filepath)
        conn.send(str(filesize).encode().ljust(16, b' '))

        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                conn.sendall(chunk)

        print(f"[S1 TCP] Arquivo enviado: {filename} ({filesize} bytes)")
        conn.close()



# Inicia apenas o servidor TCP
threading.Thread(target=tcp_server, daemon=True).start()

# Mantém processo ativo
while True:
    pass
