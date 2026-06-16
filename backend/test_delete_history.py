import urllib.request, urllib.error, json

base = 'http://localhost:5000'

def get(path):
    req = urllib.request.urlopen(base + path, timeout=5)
    return json.loads(req.read().decode())

def delete(path):
    req = urllib.request.Request(base + path, method='DELETE')
    res = urllib.request.urlopen(req, timeout=5)
    return json.loads(res.read().decode())

cats = get('/api/categories')
compls = get('/api/complaints')
print('Complaints:', len(compls))
if not compls:
    print('No complaints to test')
    raise SystemExit

c = compls[0]
print('Using complaint', c['tracking_id'])
full = get(f"/api/complaints/track/{c['tracking_id']}")
print('History entries:', len(full.get('history', [])))
if not full.get('history'):
    print('No history to delete')
else:
    hid = full['history'][0]['id']
    print('Deleting history id', hid)
    res = delete(f"/api/history/{hid}")
    print('Delete response:', res)
    new = get(f"/api/complaints/track/{c['tracking_id']}")
    print('New history count:', len(new.get('history', [])))
