import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os

# ---------------------------------------
#   DOWNLOAD VIA TCP
# ---------------------------------------
def download_tcp(host, port, filename, log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)
    
    log(f"\n[CLIENTE] Conectando via TCP em {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # Envia nome do arquivo
    s.send(filename.encode())

    # Recebe tamanho do arquivo (16 bytes)
    header = s.recv(16).decode().strip()
    if header == "NOT_FOUND":
        log("Arquivo não encontrado no servidor via TCP!")
        s.close()
        return None

    filesize = int(header)
    log(f"[CLIENTE] Tamanho do arquivo: {filesize} bytes")

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
    log("[CLIENTE] Arquivo recebido com sucesso via TCP!")
    return data


# ---------------------------------------
#   DOWNLOAD VIA UDP
# ---------------------------------------
def download_udp(host, port, filename, log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)
    
    log(f"\n[CLIENTE] Enviando solicitação UDP para {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)

    s.sendto(filename.encode(), (host, port))

    try:
        data, _ = s.recvfrom(10000000)
        log("[CLIENTE] Arquivo recebido via UDP!")
        s.close()
        return data

    except socket.timeout:
        log("[CLIENTE] Tempo limite excedido no UDP!")
        s.close()
        return None


# ---------------------------------------
#   CONSULTA AO CONTROLLER
# ---------------------------------------
def ask_controller(filename, controller_ip="127.0.0.1", log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)
    
    log(f"\n[CLIENTE] Consultando o Controller em {controller_ip}:5000...")
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
#   INTERFACE GRÁFICA
# ---------------------------------------
class ElvisClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎸 Biblioteca Elvis Presley - Cliente TCP/UDP")
        self.root.geometry("700x700")
        self.root.resizable(False, False)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores tema Elvis (azul e dourado)
        self.bg_color = "#1a1a2e"
        self.fg_color = "#eee"
        self.accent_color = "#ffd700"
        self.button_color = "#16213e"
        
        self.root.configure(bg=self.bg_color)
        
        # Título
        title_frame = tk.Frame(root, bg=self.bg_color)
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🎸 BIBLIOTECA ELVIS PRESLEY 🎸",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Cliente TCP/UDP para Download de Músicas e Letras",
            font=("Arial", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        subtitle_label.pack()
        
        # Frame principal
        main_frame = tk.Frame(root, bg=self.bg_color)
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Campo de IP do Controller
        ip_frame = tk.Frame(main_frame, bg=self.bg_color)
        ip_frame.pack(fill="x", pady=(0, 10))
        
        ip_label = tk.Label(
            ip_frame,
            text="IP do Controller:",
            font=("Arial", 10, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        ip_label.pack(side="left", padx=(0, 10))
        
        self.controller_ip = tk.StringVar(value="127.0.0.1")
        ip_entry = tk.Entry(
            ip_frame,
            textvariable=self.controller_ip,
            font=("Arial", 11),
            width=20,
            bg="#0f3460",
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="flat",
            borderwidth=2
        )
        ip_entry.pack(side="left")
        
        ip_hint = tk.Label(
            ip_frame,
            text="(localhost = 127.0.0.1)",
            font=("Arial", 9),
            bg=self.bg_color,
            fg="#888"
        )
        ip_hint.pack(side="left", padx=(10, 0))
        
        # Lista de músicas
        music_label = tk.Label(
            main_frame,
            text="Selecione uma música:",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        music_label.pack(anchor="w", pady=(0, 5))
        
        # Frame para listbox com scrollbar
        list_frame = tk.Frame(main_frame, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.music_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            height=10,
            yscrollcommand=scrollbar.set,
            bg="#0f3460",
            fg=self.fg_color,
            selectbackground=self.accent_color,
            selectforeground=self.bg_color,
            relief="flat",
            borderwidth=2
        )
        self.music_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.music_listbox.yview)
        
        # Preencher lista
        for num in sorted(MUSICAS.keys()):
            nome = MUSICAS[num][2]
            self.music_listbox.insert(tk.END, f"{num:2d}. {nome}")
        
        # Seleção de tipo
        type_label = tk.Label(
            main_frame,
            text="Selecione o tipo de arquivo:",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        type_label.pack(anchor="w", pady=(10, 5))
        
        self.file_type = tk.StringVar(value="mp4")
        
        type_frame = tk.Frame(main_frame, bg=self.bg_color)
        type_frame.pack(anchor="w", pady=(0, 10))
        
        mp4_radio = tk.Radiobutton(
            type_frame,
            text="🎵 Música (MP4)",
            variable=self.file_type,
            value="mp4",
            font=("Arial", 11),
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.button_color,
            activebackground=self.bg_color,
            activeforeground=self.accent_color
        )
        mp4_radio.pack(side="left", padx=(0, 20))
        
        txt_radio = tk.Radiobutton(
            type_frame,
            text="📝 Letra (TXT)",
            variable=self.file_type,
            value="txt",
            font=("Arial", 11),
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.button_color,
            activebackground=self.bg_color,
            activeforeground=self.accent_color
        )
        txt_radio.pack(side="left")
        
        # Botão de download
        self.download_btn = tk.Button(
            main_frame,
            text="⬇️  BAIXAR ARQUIVO",
            command=self.start_download,
            font=("Arial", 12, "bold"),
            bg=self.accent_color,
            fg=self.bg_color,
            activebackground="#ffed4e",
            activeforeground=self.bg_color,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.download_btn.pack(pady=15)
        
        # Log de status
        log_label = tk.Label(
            main_frame,
            text="Log de operações:",
            font=("Arial", 10, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        log_label.pack(anchor="w", pady=(5, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            font=("Courier", 9),
            bg="#0f3460",
            fg="#00ff00",
            relief="flat",
            borderwidth=2
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")
        
    def log(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()
    
    def start_download(self):
        """Inicia o processo de download em thread separada"""
        selection = self.music_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("Atenção", "Por favor, selecione uma música!")
            return
        
        # Obtém número da música selecionada
        index = selection[0]
        music_num = index + 1
        
        # Desabilita botão durante download
        self.download_btn.config(state="disabled", text="⏳ Baixando...")
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        
        # Inicia download em thread separada
        thread = threading.Thread(target=self.download_file, args=(music_num,))
        thread.daemon = True
        thread.start()
    
    def download_file(self, music_num):
        """Realiza o download do arquivo"""
        try:
            # Determina o filename
            if self.file_type.get() == "mp4":
                filename = MUSICAS[music_num][0]
            else:
                filename = MUSICAS[music_num][1]
            
            self.log(f"📁 Arquivo selecionado: {filename}")
            
            # Consulta o Controller
            controller_ip = self.controller_ip.get().strip()
            if not controller_ip:
                controller_ip = "127.0.0.1"
            
            info = ask_controller(filename, controller_ip, self.log)
            
            self.log(f"\n📊 Controller decidiu:")
            self.log(f"   Servidor: {info['server']}")
            self.log(f"   Host: {info['host']}")
            self.log(f"   Protocolo: {info['protocol']}")
            
            protocol = info["protocol"]
            host = info["host"]
            tcp_port = info["tcp_port"]
            udp_port = info["udp_port"]
            
            # Baixa o arquivo
            if protocol == "TCP":
                data = download_tcp(host, tcp_port, filename, self.log)
            else:
                data = download_udp(host, udp_port, filename, self.log)
            
            if not data:
                self.log("\n❌ ERRO: Não foi possível baixar o arquivo.")
                messagebox.showerror("Erro", "Não foi possível baixar o arquivo!")
                return
            
            # Salva o arquivo
            outname = "baixado_" + filename
            with open(outname, "wb") as f:
                f.write(data)
            
            self.log(f"\n✅ Arquivo salvo como: {outname}")
            self.log(f"📊 Tamanho: {len(data)} bytes")
            self.log("🎉 Download concluído com sucesso!")
            
            messagebox.showinfo(
                "Sucesso!",
                f"Arquivo baixado com sucesso!\n\nSalvo como: {outname}\nTamanho: {len(data)} bytes"
            )
            
        except Exception as e:
            self.log(f"\n❌ ERRO: {str(e)}")
            messagebox.showerror("Erro", f"Erro durante o download:\n{str(e)}")
        
        finally:
            # Reabilita botão
            self.download_btn.config(state="normal", text="⬇️  BAIXAR ARQUIVO")


# ---------------------------------------
#   PROGRAMA PRINCIPAL
# ---------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ElvisClientGUI(root)
    root.mainloop()
