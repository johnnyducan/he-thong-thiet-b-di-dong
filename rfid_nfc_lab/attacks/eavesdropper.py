#!/usr/bin/env python3
import socket, json, time
from datetime import datetime
from colorama import Fore, init
import requests

init(autoreset=True)

CAPTURE_FILE = 'uid_capture.json'
captured_uids = []

def send_to_dashboard(proto, msg, cls):
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        requests.post('http://127.0.0.1:8080/api/log', json={
            't': now, 'proto': proto, 'msg': msg, 'cls': cls
        }, timeout=0.5)
    except:
        pass

def sniff_rfid():
    s = socket.socket()
    s.settimeout(2)
    s.connect(('127.0.0.1', 6001))
    s.send(json.dumps({'cmd': 'QUERY'}).encode())
    resp = json.loads(s.recv(512).decode())
    s.close()
    return resp

def sniff_nfc():
    s = socket.socket()
    s.settimeout(2)
    s.connect(('127.0.0.1', 6011))
    s.send(json.dumps({'cmd': 'GET_UID'}).encode())
    uid_resp = json.loads(s.recv(512).decode())
    s.close()

    s2 = socket.socket()
    s2.settimeout(2)
    s2.connect(('127.0.0.1', 6011))
    s2.send(json.dumps({'cmd': 'READ_NDEF'}).encode())
    ndef_resp = json.loads(s2.recv(2048).decode())
    s2.close()
    return uid_resp, ndef_resp

print(f'{Fore.RED}[EAVESDROP] Starting passive scan...')
print(f'{Fore.RED}[EAVESDROP] Target: RFID 6001, NFC 6011\n')

for i in range(5):
    ts = datetime.now().strftime('%H:%M:%S.%f')[:12]
    try:
        rfid = sniff_rfid()
        uid = rfid.get('uid', 'N/A')
        print(f'{Fore.RED}[{ts}] RFID CAPTURED: UID={uid} type={rfid.get("type")}')
        captured_uids.append({'ts': ts, 'proto': 'RFID', 'uid': uid})
        send_to_dashboard('RFID', f'EAVESDROP captured UID={uid}', 'EAVESDROP')
    except Exception:
        pass

    try:
        uid_r, ndef_r = sniff_nfc()
        nfc_uid = uid_r.get('uid', 'N/A')
        records = ndef_r.get('records', [])
        print(f'{Fore.RED}[{ts}] NFC CAPTURED: UID={nfc_uid}')
        for rec in records:
            print(f' -> {rec["type"]}: {rec.get("value", rec.get("data", ""))[:60]}')
        captured_uids.append({'ts': ts, 'proto': 'NFC', 'uid': nfc_uid, 'ndef': records})
        send_to_dashboard('NFC', f'EAVESDROP captured NFC UID={nfc_uid}', 'EAVESDROP')
    except Exception:
        pass

    time.sleep(1)

with open(CAPTURE_FILE, 'w') as f:
    json.dump(captured_uids, f, indent=2)
print(f'\n{Fore.RED}[EAVESDROP] Saved {len(captured_uids)} captures to {CAPTURE_FILE}')

print(f'{Fore.RED}[EAVESDROP] Starting passive scan...')
print(f'{Fore.RED}[EAVESDROP] Target: RFID:6001 / NFC:6011\n')

while True:  # <--- Đổi thành while True
    ts = datetime.now().strftime('%H:%M:%S.%f')[:12]
    # ... (các đoạn code try...except bên trong giữ nguyên) ...
    
    time.sleep(5)  # <--- Đổi thành 5 giây