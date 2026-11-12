#!/usr/bin/env python3
import socket, json, time, threading
import requests
from datetime import datetime
from colorama import Fore, init
init(autoreset=True)

HOST = '127.0.0.1'
PORT = 7001

CARD_DB = {
    'A1B2C3D4E5': {'owner': 'Nguyen Van A', 'level': 'EMPLOYEE', 'active': True},
    'DEADBEEF01': {'owner': 'Tran Thi B', 'level': 'ADMIN', 'active': True},
    'CAFEBABE02': {'owner': 'Le Van C', 'level': 'GUEST', 'active': True},
}

SEEN_UIDS = []
access_log = []

class AccessControlServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(10)
        print(f"{Fore.GREEN}[AC] Access Control Server @ {HOST}:{PORT}")
        print(f"{Fore.CYAN}[AC] Loaded {len(CARD_DB)} cards in database")

    def handle(self, conn, addr):
        try:
            import requests # Đảm bảo thư viện requests được nạp
            data = conn.recv(512)
            req = json.loads(data.decode())
            uid = req.get('uid', '')
            ts = req.get('timestamp', 0)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if uid in CARD_DB and CARD_DB[uid]['active']:
                card = CARD_DB[uid]
                resp = {
                    'status': 'GRANTED',
                    'owner': card['owner'],
                    'level': card['level'],
                    'time': now,
                }
                entry = f"{now} GRANTED uid={uid} owner={card['owner']}"
                print(f"{Fore.GREEN}[AC] {entry}")
            else:
                resp = {'status': 'DENIED', 'msg': f'UID {uid} not authorized!'}
                entry = f"{now} DENIED uid={uid}"
                print(f"{Fore.RED}[AC] {entry}")
            
            access_log.append(entry)
            
            # --- ĐOẠN CODE THÊM VÀO ĐỂ ĐẨY EVENT LÊN DASHBOARD ---
            try:
                requests.post('http://127.0.0.1:8080/api/log', json={
                    't': now,
                    'proto': 'RFID',
                    'msg': entry,
                    'cls': 'GRANTED' if 'GRANTED' in entry else 'DENIED'
                }, timeout=1)
            except:
                pass # Bỏ qua nếu chưa bật Dashboard để không làm sập Server
            # -----------------------------------------------------
            
            conn.send(json.dumps(resp).encode())
        except Exception as e:
            print(f"{Fore.RED}[AC] Error: {e}")
        finally:
            conn.close()

    def run(self):
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    AccessControlServer().run()
