import socket
import os
import json

# ------------------------------------------------------------
# Função: descobrir automaticamente o IP da máquina no Wi-Fi
# ------------------------------------------------------------
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # não envia nada, só descobre o IP real
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


MACHINE_IP = get_local_ip()
print(f"[CONTROLLER] IP detectado: {MACHINE_IP}")


# ------------------------------------------------------------
# Servidores S1 e S2 (tolerância a falha)
# ------------------------------------------------------------
SERVERS = {
    "S1": {"host": MACHINE_IP, "tcp_port": 6001, "udp_port": 6002},
    "S2": {"host": MACHINE_IP, "tcp_port": 7001, "udp_port": 7002}
}

# Os dois servidores possuem todos os arquivos
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
# Verifica se servidor está online
# ------------------------------------------------------------
def servidor_online(host, port):
    try:
        s = socket.create_connection((host, port), timeout=0.4)
        s.close()
        return True
    except:
        return False


# ------------------------------------------------------------
# Decide qual servidor será usado (com failover S1 → S2)
# ------------------------------------------------------------
def escolher_servidor(filename):
    servidores = FILES[filename]  # sempre ["S1", "S2"]

    # Testa S1 primeiro
    s1 = servidores[0]
    info1 = SERVERS[s1]

    if servidor_online(info1["host"], info1["tcp_port"]):
        print("[CONTROLLER] S1 está ativo. Usando S1.")
        return s1

    # S1 caiu → tenta S2
    s2 = servidores[1]
    info2 = SERVERS[s2]

    if servidor_online(info2["host"], info2["tcp_port"]):
        print("[CONTROLLER] S1 offline. Failover → S2.")
        return s2

    # Nenhum está ativo
    print("[CONTROLLER] ERRO: Nenhum servidor está disponível.")
    return None


# ------------------------------------------------------------
# Decide se será TCP ou UDP baseado no tamanho do arquivo
# ------------------------------------------------------------
def decide_protocol(filename):
    path = os.path.join(os.path.dirname(__file__), "conteudo_server1", "files", filename)
    size = os.path.getsize(path)

    return "UDP" if size <= 7000 else "TCP"


# ------------------------------------------------------------
# Controller principal
# ------------------------------------------------------------
def start_controller():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 5000))  # aceita requisições do cliente na rede Wi-Fi
    s.listen(5)
    print("[CONTROLLER] Rodando na porta 5000...")

    while True:
        conn, addr = s.accept()
        filename = conn.recv(1024).decode().strip()

        if filename not in FILES:
            conn.send(b"ERROR_FILE_NOT_FOUND")
            conn.close()
            continue

        # Seleciona S1 ou S2 automaticamente (tolerância a falhas)
        server_key = escolher_servidor(filename)

        if server_key is None:
            conn.send(b"ERROR_NO_SERVERS_AVAILABLE")
            conn.close()
            continue

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
