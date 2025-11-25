import socket
import json
import os
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# ---------------------------------------
# DOWNLOAD VIA TCP
# ---------------------------------------
def download_tcp(host, port, filename):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(filename.encode())

        header = s.recv(16).decode().strip()

        if not header or header == "NOT_FOUND":
            s.close()
            return None

        size = int(header)
        data = b""
        remaining = size

        while remaining > 0:
            chunk = s.recv(min(4096, remaining))
            if not chunk:
                break
            data += chunk
            remaining -= len(chunk)

        s.close()
        return data

    except Exception as e:
        print("[ERRO TCP]", e)
        return None


# ---------------------------------------
# DOWNLOAD VIA UDP
# ---------------------------------------
def download_udp(host, port, filename):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        s.sendto(filename.encode(), (host, port))
        data, _ = s.recvfrom(10000000)
        s.close()
        return data
    except Exception as e:
        print("[ERRO UDP]", e)
        return None


# ---------------------------------------
# CONSULTA AO CONTROLLER (com validação)
# ---------------------------------------
def ask_controller(filename, controller_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((controller_ip, 5000))
    s.send(filename.encode())

    raw = s.recv(4096).decode().strip()
    s.close()

    # Segurança: controller sempre deve retornar JSON
    if not raw.startswith("{"):
        raise Exception(f"Resposta inválida do controller: {raw}")

    return json.loads(raw)


# ---------------------------------------
# MÚSICAS
# ---------------------------------------
MUSICAS = {
    1: ("jailhouse_rock.mp4", "jailhouse_rock.txt", "Jailhouse Rock"),
    2: ("cant_help_falling_in_love.mp4", "cant_help_falling_in_love.txt", "Can't Help Falling In Love"),
    3: ("hound_dog.mp4", "hound_dog.txt", "Hound Dog"),
    4: ("blue_suede_shoes.mp4", "blue_suede_shoes.txt", "Blue Suede Shoes"),
    5: ("suspicious_minds.mp4", "suspicious_minds.txt", "Suspicious Minds"),
    6: ("love_me_tender.mp4", "love_me_tender.txt", "Love Me Tender"),
    7: ("heartbreak_hotel.mp4", "heartbreak_hotel.txt", "Heartbreak Hotel"),
    8: ("burning_love.mp4", "burning_love.txt", "Burning Love"),
    9: ("all_shook_up.mp4", "all_shook_up.txt", "All Shook Up"),
    10: ("in_the_ghetto.mp4", "in_the_ghetto.txt", "In The Ghetto"),
    11: ("thats_all_right.mp4", "thats_all_right.txt", "That's All Right")
}


# ---------------------------------------
# ROTAS WEB
# ---------------------------------------
@app.route('/')
def index():
    return render_template('index.html', musicas=MUSICAS)


@app.route('/download', methods=['POST'])
def download():
    try:
        req = request.json
        music_num = int(req['music_num'])
        file_type = req['file_type']
        controller_ip = req['controller_ip']

        # Seleção do arquivo correto
        filename = MUSICAS[music_num][0] if file_type == 'mp4' else MUSICAS[music_num][1]

        # Consulta controller
        info = ask_controller(filename, controller_ip)

        # Download conforme protocolo
        if info["protocol"] == "TCP":
            file_data = download_tcp(info["host"], info["tcp_port"], filename)
        else:
            file_data = download_udp(info["host"], info["udp_port"], filename)

        if not file_data:
            return jsonify({"error": "Falha no download do servidor"}), 500

        # Salvar temporário
        temp_path = f"temp_{filename}"
        with open(temp_path, "wb") as f:
            f.write(file_data)

        return jsonify({
            "success": True,
            "filename": filename,
            "size": len(file_data),
            "protocol": info["protocol"],
            "server": info["server"],
            "download_url": f"/get_file/{temp_path}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_file/<path:filename>')
def get_file(filename):
    if not os.path.exists(filename):
        return "Arquivo não existe mais no servidor.", 404
    return send_file(filename, as_attachment=True, download_name=filename.replace("temp_", "baixado_"))


# ---------------------------------------
# INICIAR SERVIDOR
# ---------------------------------------
if __name__ == '__main__':
    # Descobrir IP local
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except:
        local_ip = "127.0.0.1"
    finally:
        s.close()

    print("=" * 60)
    print("SERVIDOR WEB ELVIS PRESLEY INICIADO!")
    print("=" * 60)
    print(f"Acesse pelo PC: http://127.0.0.1:8080")
    print(f"Acesse pelo celular: http://{local_ip}:8080")
    print("=" * 60)

    app.run(host='0.0.0.0', port=8080, debug=False)
