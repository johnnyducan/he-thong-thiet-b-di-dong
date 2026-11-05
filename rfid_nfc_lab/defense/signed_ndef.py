#!/usr/bin/env python3
import ndef, hmac, hashlib, json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

SIGNING_KEY = b'NDEFSigningKey_AES256_2024_Lab!'

def sign_ndef(uri: str) -> dict:
    record = ndef.UriRecord(uri)
    ndef_raw = b''.join(ndef.message_encoder([record]))
    nonce = get_random_bytes(8).hex()
    payload = ndef_raw.hex() + ':' + nonce
    sig = hmac.new(SIGNING_KEY, payload.encode(), hashlib.sha256).hexdigest()
    return {'ndef_hex': ndef_raw.hex(), 'nonce': nonce, 'sig': sig}

def verify_ndef(signed_pkg: dict) -> bool:
    payload = signed_pkg['ndef_hex'] + ':' + signed_pkg['nonce']
    expected = hmac.new(SIGNING_KEY, payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signed_pkg['sig'])

if __name__ == '__main__':
    pkg = sign_ndef('https://iotlab.edu.vn/checkin')
    print('Signed package:', json.dumps(pkg, indent=2))
    print('Verify legit:', verify_ndef(pkg))
    pkg['ndef_hex'] = 'deadbeef'
    print('Verify tampered:', verify_ndef(pkg))
