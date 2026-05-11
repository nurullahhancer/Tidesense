import httpx
base = "http://localhost:8000/api/v1"
t = httpx.post(f"{base}/auth/login", json={"username":"tidesense","password":"tidesense123"}).json()["access_token"]
h = {"Authorization": f"Bearer {t}"}
users = httpx.get(f"{base}/users", headers=h).json()
for u in users:
    if u["username"] in ["test_user_temp", "admin2_temp"]:
        r = httpx.delete(f"{base}/users/{u['id']}", headers=h)
        print(f"Deleted {u['username']} -> {r.status_code}")
print("Done")
