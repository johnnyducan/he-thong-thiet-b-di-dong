#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string, request
import socket, threading, time, collections, json as _json

app = Flask(__name__)
events = collections.deque(maxlen=300)
stats = {
    'rfid_scans': 0,
    'nfc_reads': 0,
    'granted': 0,
    'denied': 0,
    'replay_blocked': 0,
    'ndef_injected': 0,
    'eavesdrop': 0
}

HTML = """<!DOCTYPE html><html>
<head><meta charset="UTF-8">
<title>RFID/NFC Security Monitor</title>
<style>
body { background:#0f172a; color:#e2e8f0; font-family:monospace; margin:20px; }
h1 { color:#38bdf8; }
.stats { display: flex; gap:20px; margin-bottom:20px; }
.card { background:#1e293b; padding:16px; border-radius: 8px; min-width:120px; text-align:center; }
.card .val { font-size:2em; font-weight:bold; color: #22d3ee; }
.card .lbl { font-size:0.8em; color:#94a3b8; }
.GRANTED { color: #4ade80; }
.DENIED { color:#f87171; }
.EAVESDROP { color:#fb923c; }
.REPLAY { color: #f43f5e; font-weight:bold; }
.INJECT { color:#e879f9; font-weight:bold; }
.NORMAL { color:#94a3b8; }
#log { height:500px; overflow-y:auto; background:#0f172a; padding: 8px; border: 1px solid #1e293b; }
.entry { border-bottom:1px solid #1e293b; padding: 4px 0; }
</style></head>
<body>
<h1>RFID / NFC Security Monitor</h1>
<div class="stats" id="stats"></div>
<h3>Live Event Log</h3>
<div id="log"></div>
<script>
function update() {
    fetch('/api/events').then(r=>r.json()).then(d=>{
        document.getElementById('log').innerHTML = d.events.slice(-50).reverse()
            .map(e=>`<div class="entry"><span class="${e.cls}">[${e.t}] [${e.proto}] ${e.msg}</span></div>`).join('');
        const s = d.stats;
        document.getElementById('stats').innerHTML = `
            <div class="card"><div class="val">${s.rfid_scans}</div><div class="lbl">RFID Scans</div></div>
            <div class="card"><div class="val" style="color:#4ade80">${s.granted}</div><div class="lbl">Granted</div></div>
            <div class="card"><div class="val" style="color:#f87171">${s.denied}</div><div class="lbl">Denied</div></div>
            <div class="card"><div class="val" style="color:#f43f5e">${s.replay_blocked}</div><div class="lbl">Replay Blocked</div></div>
            <div class="card"><div class="val" style="color:#e879f9">${s.ndef_injected}</div><div class="lbl">NDEF Injected</div></div>
        `;
    });
}
update(); setInterval(update, 1500);
</script></body></html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/events')
def api_events():
    return jsonify({'events': list(events), 'stats': stats})

@app.route('/api/log', methods=['POST'])
def api_log():
    data = request.json
    events.append(data)
    proto = data.get('proto', '')
    msg = data.get('msg', '')
    if 'RFID' in proto: stats['rfid_scans'] += 1
    if 'NFC' in proto: stats['nfc_reads'] += 1
    if 'GRANTED' in msg: stats['granted'] += 1
    if 'DENIED' in msg: stats['denied'] += 1
    if 'REPLAY' in msg: stats['replay_blocked'] += 1
    if 'NDEF' in msg: stats['ndef_injected'] += 1
    return jsonify({'ok': True})

if __name__ == '__main__':
    print('[Dashboard] Running @ http://localhost:8080')
    app.run(host='0.0.0.0', port=8080, debug=False)
