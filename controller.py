import socket
import os
import json

# ------------------------------------------------------------
# Função para obter automaticamente o IP da máquina no Wi-Fi
# ------------------------------------------------------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Não envia nada, só abre conexão para descobrir o IP real
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


# IP REAL DA MÁQUINA (dinâmico, funciona em qualquer Wi-Fi)
MACHINE_IP = get_local_ip()
print(f"[CONTROLLER] IP detectado na rede Wi-Fi: {MACHINE_IP}")

# ------------------------------------------------------------
# Definição dos servidores usando o IP real automático
# ------------------------------------------------------------
SERVERS = {
    "S1": {"host": MACHINE_IP, "tcp_port": 6001, "udp_port": 6002},
    "S2": {"host": MACHINE_IP, "tcp_port": 7001, "udp_port": 7002}
}

# Todos servidores têm todos os arquivos
FILES = {
    "jailhouse_rock.mp4": ["S1", "S2"],
    "jailhouse_rock.txt": ["S1", "S2"],

    "cant_help_falling_in_love.mp4": ["S1", "S2"],
    "cant_help_falling_in_love.txt": ["S1", "S2"],

    "hound_dog.mp4": ["S1", "S2"],
    "hound_dog.txt": ["S1", "S2"],

    "blue_suede_shoes.mp4": ["S1", "S2"],
    "blue_suede_shoes.txt": ["S1", "S2"],

    "suspicious_minds.mp4": ["S1", "S2"],
    "suspicious_minds.txt": ["S1", "S2"],

    "love_me_tender.mp4": ["S1", "S2"],
    "love_me_tender.txt": ["S1", "S2"],

    "heartbreak_hotel.mp4": ["S1", "S2"],
    "heartbreak_hotel.txt": ["S1", "S2"],

    "burning_love.mp4": ["S1", "S2"],
    "burning_love.txt": ["S1", "S2"],

    "all_shook_up.mp4": ["S1", "S2"],
    "all_shook_up.txt": ["S1", "S2"],

    "in_the_ghetto.mp4": ["S1", "S2"],
    "in_the_ghetto.txt": ["S1", "S2"],

    "thats_all_right.mp4": ["S1", "S2"],
    "thats_all_right.txt": ["S1", "S2"],
}


# ------------------------------------------------------------
# Decide se será TCP ou UDP
# ------------------------------------------------------------
def decide_protocol(filename):
    # Resolve path relative to this controller script so size checks work
    path = os.path.join(os.path.dirname(__file__), "conteudo_server1", "files", filename)
    size = os.path.getsize(path)

    if size <= 7000:
        return "UDP"
    return "TCP"

# ------------------------------------------------------------
# Controller principal
# ------------------------------------------------------------
def start_controller():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Aceita conexões de QUALQUER IP da rede
    s.bind(("0.0.0.0", 5000))
    s.listen(5)
    print("[CONTROLLER] Rodando na porta 5000...")

    while True:
        conn, addr = s.accept()
        filename = conn.recv(1024).decode().strip()

        if filename not in FILES:
            conn.send(b"ERROR_FILE_NOT_FOUND")
            conn.close()
            continue

        # Escolhe servidor (S1)
        server_key = FILES[filename][0]
        server = SERVERS[server_key]

        protocol = decide_protocol(filename)

        payload = json.dumps({
            "server": server_key,
            "host": server["host"],
            "tcp_port": server["tcp_port"],
            "udp_port": server["udp_port"],
            "protocol": protocol
        }).encode()

        conn.send(payload)
        conn.close()

start_controller()
