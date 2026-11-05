#!/usr/bin/env python3
import socket, json, time

def rfid_query():
    s = socket.socket()
    s.settimeout(2)
    s.connect(('127.0.0.1', 6001))
    s.send(json.dumps({'cmd': 'QUERY'}).encode())
    r = json.loads(s.recv(512).decode())
    s.close()
    return r

def ac_auth(uid):
    s = socket.socket()
    s.settimeout(2)
    s.connect(('127.0.0.1', 7001))
    s.send(json.dumps({'cmd': 'AUTH', 'uid': uid, 'timestamp': time.time()}).encode())
    r = json.loads(s.recv(512).decode())
    s.close()
    return r

print('=== RFID Access Control Integration Test ===')
for attempt in range(3):
    print(f'\n[Attempt {attempt+1}] Scanning tag...')
    tag = rfid_query()
    if tag.get('status') == 'TAG_PRESENT':
        uid = tag['uid']
        print(f'Tag UID: {uid}')
        result = ac_auth(uid)
        status = result.get('status')
        print(f'Result: {status} ({result.get("owner", result.get("msg"))})')
    time.sleep(1)
