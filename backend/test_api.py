import urllib.request, urllib.error, json, sys

base = "http://localhost:5000"
passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        result = fn()
        print(f"  [PASS] {name}: {result}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        failed += 1

def get(path):
    req = urllib.request.urlopen(base + path, timeout=5)
    return json.loads(req.read().decode("utf-8"))

def post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(base + path, data=data,
          headers={"Content-Type": "application/json"}, method="POST")
    res = urllib.request.urlopen(req, timeout=5)
    return json.loads(res.read().decode("utf-8"))

def patch(path, body, token=None):
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token: headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(base + path, data=data, headers=headers, method="PATCH")
    res = urllib.request.urlopen(req, timeout=5)
    return json.loads(res.read().decode("utf-8"))

print("\n" + "="*55)
print("  COMPLAIN BOX - API TEST SUITE")
print("="*55)

# 1. Health check
test("Health check", lambda: get("/")["message"][:30])

# 2. Categories
cats = None
def t2():
    global cats
    cats = get("/api/categories")
    return f"{len(cats)} categories loaded"
test("Categories", t2)

# 3. Submit complaint
tracking_id = None
def t3():
    global tracking_id
    res = post("/api/complaints", {
        "title": "AC not working in Lab 3",
        "description": "The AC in Computer Lab 3 has been broken for 2 weeks.",
        "category_id": 1,
        "priority": "high",
        "is_anonymous": True,
        "submitter_email": None
    })
    tracking_id = res["tracking_id"]
    return f"Tracking ID = {tracking_id}"
test("Submit complaint", t3)

# 4. Track by ID
def t4():
    res = get(f"/api/complaints/track/{tracking_id}")
    return f"Status={res['status']}, History={len(res['history'])} entries"
test("Track complaint", t4)

# 5. Submit 2nd complaint (different category)
def t5():
    res = post("/api/complaints", {
        "title": "Library books not returned policy unclear",
        "description": "Students are confused about the fine policy for late returns.",
        "category_id": 7,
        "priority": "medium",
        "is_anonymous": True
    })
    return f"Tracking ID = {res['tracking_id']}"
test("Submit 2nd complaint", t5)

# 6. Dashboard stats
def t6():
    d = get("/api/dashboard/stats")
    return f"Total={d['total']}, Pending={d['pending']}, Categories={len(d['by_category'])}"
test("Dashboard stats", t6)

# 7. List all complaints
def t7():
    res = get("/api/complaints")
    return f"{len(res)} complaints returned"
test("List all complaints", t7)

# 8. Admin login
token = None
def t8():
    global token
    res = post("/api/auth/login", {"username": "shine", "password": "262425"})
    token = res["token"]
    return f"Logged in as {res['user']['username']} ({res['user']['role']})"
test("Admin login", t8)

# 9. Wrong password
def t9():
    try:
        post("/api/auth/login", {"username": "admin", "password": "wrong"})
        return "ERROR: should have failed"
    except urllib.error.HTTPError as e:
        return f"Correctly rejected (HTTP {e.code})"
test("Wrong password rejected", t9)

# 10. Update status
def t10():
    complaints = get("/api/complaints")
    cid = complaints[0]["id"]
    res = patch(f"/api/complaints/{cid}/status", {
        "status": "in_progress",
        "note": "Assigned to maintenance team",
    }, token=token)
    return f"Status -> {res['complaint']['status']}"
test("Update status to in_progress", t10)

# 11. Resolve complaint
def t11():
    complaints = get("/api/complaints")
    cid = complaints[0]["id"]
    res = patch(f"/api/complaints/{cid}/status", {
        "status": "resolved",
        "note": "AC repaired and tested OK",
    }, token=token)
    return f"Status -> {res['complaint']['status']}"
test("Resolve complaint", t11)

# 12. Check timeline
def t12():
    res = get(f"/api/complaints/track/{tracking_id}")
    return f"{len(res['history'])} timeline entries"
test("Timeline has entries", t12)

print("\n" + "="*55)
print(f"  Results: {passed} PASSED  |  {failed} FAILED")
print("="*55 + "\n")

sys.exit(0 if failed == 0 else 1)
