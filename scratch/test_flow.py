import urllib.request
import json

BASE = 'http://127.0.0.1:8000'

# 1. Reset mode to supervised for test
req = urllib.request.Request(f'{BASE}/api/sre/mode', data=json.dumps({'mode': 'supervised'}).encode(), headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
print('Set SRE mode supervised:', res.read().decode())

# 2. Inject GCP proxy timeout failure scenario
req = urllib.request.Request(f'{BASE}/api/demo/inject-scenario', data=json.dumps({'scenario_id': 'gcp_proxy_timeout'}).encode(), headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
print('Injected scenario response:', res.read().decode())

# 3. Fetch incidents and inspect the active incident
res = urllib.request.urlopen(f'{BASE}/api/incidents')
data = json.loads(res.read().decode())
incidents = data.get('incidents', [])
active_incidents = [i for i in incidents if i.get('status') == 'ACTIVE']
print(f"Total incidents: {len(incidents)}, Active incidents: {len(active_incidents)}")
if active_incidents:
    top = active_incidents[0]
    print(f"Top active: {top['incident_id']} - {top['title']} (requires_approval: {top.get('requires_approval')})")
    
    # 4. Approve the top incident
    top_id = top['incident_id']
    req = urllib.request.Request(f'{BASE}/api/incident/{top_id}/approve', data=b'', headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    print('Approved incident response:', res.read().decode())

# 5. Verify dashboard summary
res = urllib.request.urlopen(f'{BASE}/api/dashboard/summary')
summary = json.loads(res.read().decode())
print(f"Dashboard Summary -> status: {summary['status']}, score: {summary['health_score']}, errors: {summary['counts']['error']}")

# 6. Test Autonomous mode switch auto-heals
# Inject scenario again
req = urllib.request.Request(f'{BASE}/api/demo/inject-scenario', data=json.dumps({'scenario_id': 'aws_cpu_spike'}).encode(), headers={'Content-Type': 'application/json'})
urllib.request.urlopen(req)

# Switch to autonomous mode
req = urllib.request.Request(f'{BASE}/api/sre/mode', data=json.dumps({'mode': 'autonomous'}).encode(), headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
print('Autonomous mode switch result:', res.read().decode())

# Verify dashboard summary again
res = urllib.request.urlopen(f'{BASE}/api/dashboard/summary')
summary = json.loads(res.read().decode())
print(f"After Autonomous Mode -> status: {summary['status']}, score: {summary['health_score']}, errors: {summary['counts']['error']}")
