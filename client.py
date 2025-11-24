import socket
import json

# ---------------------------------------
#   DOWNLOAD VIA TCP
# ---------------------------------------
def download_tcp(host, port, filename):
    print(f"\n[CLIENTE] Conectando via TCP em {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # Envia nome do arquivo
    s.send(filename.encode())

    # Recebe tamanho do arquivo (16 bytes)
    header = s.recv(16).decode().strip()
    if header == "NOT_FOUND":
        print("Arquivo não encontrado no servidor via TCP!")
        s.close()
        return None

    filesize = int(header)
    print(f"[CLIENTE] Tamanho do arquivo: {filesize} bytes\n")

    # Recebe conteúdo
    data = b""
    remaining = filesize

    while remaining > 0:
        chunk = s.recv(min(4096, remaining))
        if not chunk:
            break
        data += chunk
        remaining -= len(chunk)

    s.close()
    print("[CLIENTE] Arquivo recebido com sucesso via TCP!")
    return data


# ---------------------------------------
#   DOWNLOAD VIA UDP
# ---------------------------------------
def download_udp(host, port, filename):
    print(f"\n[CLIENTE] Enviando solicitação UDP para {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)

    s.sendto(filename.encode(), (host, port))

    try:
        data, _ = s.recvfrom(10000000)
        print("[CLIENTE] Arquivo recebido via UDP!")
        s.close()
        return data

    except socket.timeout:
        print("[CLIENTE] Tempo limite excedido no UDP!")
        s.close()
        return None


# ---------------------------------------
#   CONSULTA AO CONTROLLER
# ---------------------------------------
def ask_controller(filename, controller_ip="127.0.0.1"):
    print(f"\n[CLIENTE] Consultando o Controller em {controller_ip}:5000...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((controller_ip, 5000))
    s.send(filename.encode())

    data = s.recv(4096)
    s.close()

    return json.loads(data.decode())


# ---------------------------------------
#   LISTA DE MÚSICAS DISPONÍVEIS
# ---------------------------------------

MUSICAS = {
    1: ("jailhouse_rock.mp4", "jailhouse_rock.txt"),
    2: ("cant_help_falling_in_love.mp4", "cant_help_falling_in_love.txt"),
    3: ("hound_dog.mp4", "hound_dog.txt"),
    4: ("blue_suede_shoes.mp4", "blue_suede_shoes.txt"),
    5: ("suspicious_minds.mp4", "suspicious_minds.txt"),
    6: ("love_me_tender.mp4", "love_me_tender.txt"),
    7: ("heartbreak_hotel.mp4", "heartbreak_hotel.txt"),
    8: ("burning_love.mp4", "burning_love.txt"),
    9: ("all_shook_up.mp4", "all_shook_up.txt"),
    10: ("in_the_ghetto.mp4", "in_the_ghetto.txt"),
    11: ("thats_all_right.mp4", "thats_all_right.txt")
}

# ---------------------------------------
#   PROGRAMA PRINCIPAL
# ---------------------------------------
if __name__ == "__main__":

    print("=== BIBLIOTECA DO ELVIS PRESLEY ===\n")
    
    # Configuração do IP do Controller
    controller_ip = input("IP do Controller (Enter para localhost): ").strip()
    if not controller_ip:
        controller_ip = "127.0.0.1"
    
    print("\nEscolha o número da música:")

    for num, (mp4, txt) in MUSICAS.items():
        nome = mp4.replace(".mp4","").replace("_"," ").title()
        print(f"{num} - {nome}")

    escolha = int(input("\nDigite o número da música: "))

    print("\n1 - Baixar MÚSICA (MP4)")
    print("2 - Baixar LETRA (TXT)")
    t = input("Escolha: ")

    if t == "1":
        filename = MUSICAS[escolha][0]
    else:
        filename = MUSICAS[escolha][1]

    # Consulta o Controller
    info = ask_controller(filename, controller_ip)

    print("\n[CLIENTE] Controller decidiu:")
    print(info)

    protocol = info["protocol"]
    host = info["host"]
    tcp_port = info["tcp_port"]
    udp_port = info["udp_port"]

    # Baixa o arquivo
    if protocol == "TCP":
        data = download_tcp(host, tcp_port, filename)
    else:
        data = download_udp(host, udp_port, filename)

    if not data:
        print("\n[CLIENTE] ERRO: Não foi possível baixar o arquivo.")
        exit()

    outname = "baixado_" + filename
    with open(outname, "wb") as f:
        f.write(data)

    print(f"\n[CLIENTE] Arquivo salvo como: {outname}")
    print("[CLIENTE] Finalizado com sucesso!")
