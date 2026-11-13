#!/usr/bin/env python3
# usage: arckit-mcp-call TOOL '<args-json>'   (defaults: arckit.check_gates {"project_id":"001-spp"})
import json, subprocess, sys
BIN = '/home/terry/.local/share/arckit-mcp/bin/arckit-mcp'
tool = sys.argv[1] if len(sys.argv) > 1 else 'arckit.check_gates'
args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {'project_id': '001-spp'}
p = subprocess.Popen([BIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
def send(o): p.stdin.write((json.dumps(o) + chr(10)).encode()); p.stdin.flush()
send({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'cli','version':'1'}}})
json.loads(p.stdout.readline())
send({'jsonrpc':'2.0','method':'notifications/initialized'})
send({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':tool,'arguments':args}})
for line in p.stdout:
    m = json.loads(line)
    if m.get('id') == 2:
        r = m.get('result') or m.get('error')
        print(json.dumps(r, indent=2)[:4000]); break
p.terminate()