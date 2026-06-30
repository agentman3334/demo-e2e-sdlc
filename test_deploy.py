import urllib.request
import json

data = json.dumps({"email": "test@pms.com", "password": "Test1234", "full_name": "Test User"}).encode()
req = urllib.request.Request("http://localhost:8000/api/auth/register", data=data, headers={"Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req)
    print("REGISTER:", resp.read().decode())
except urllib.error.HTTPError as e:
    print("REGISTER ERROR:", e.code, e.read().decode())

data2 = json.dumps({"email": "test@pms.com", "password": "Test1234"}).encode()
req2 = urllib.request.Request("http://localhost:8000/api/auth/login", data=data2, headers={"Content-Type": "application/json"})
try:
    resp2 = urllib.request.urlopen(req2)
    print("LOGIN:", resp2.read().decode())
except urllib.error.HTTPError as e:
    print("LOGIN ERROR:", e.code, e.read().decode())

try:
    resp3 = urllib.request.urlopen("http://localhost:80")
    print("FRONTEND:", resp3.status, "OK")
except Exception as e:
    print("FRONTEND ERROR:", e)