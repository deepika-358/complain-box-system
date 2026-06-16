import urllib.request, urllib.error, json

base = 'http://localhost:5000'

def get(path):
    req = urllib.request.urlopen(base + path, timeout=5)
    return json.loads(req.read().decode())

def delete(path):
    req = urllib.request.Request(base + path, method='DELETE')
    res = urllib.request.urlopen(req, timeout=5)
    return json.loads(res.read().decode())

# Get initial count
stats1 = get('/api/dashboard/stats')
print('Before delete - Total complaints:', stats1['total'])

# Get a complaint to delete
compls = get('/api/complaints')
if compls:
    cid = compls[0]['id']
    tid = compls[0]['tracking_id']
    print(f'Deleting complaint {tid} (id={cid})')
    res = delete(f'/api/complaints/{cid}')
    print('Delete response:', res)
    
    # Check counts after
    stats2 = get('/api/dashboard/stats')
    print('After delete - Total complaints:', stats2['total'])
    print(f'Deleted count: {stats1["total"] - stats2["total"]} (should be 1)')
else:
    print('No complaints to delete')
