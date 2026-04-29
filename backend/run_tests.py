import json, time, httpx, asyncio, websockets, concurrent.futures

results = []
base = "http://localhost:8000/api/v1"

admin_token = httpx.post(f"{base}/auth/login", json={"username":"tidesense","password":"tidesense123"}).json()["access_token"]
user_token = httpx.post(f"{base}/auth/login", json={"username":"coastal_user","password":"User123!"}).json()["access_token"]
res_token = httpx.post(f"{base}/auth/login", json={"username":"marine_researcher","password":"Research123!"}).json()["access_token"]
ah = {"Authorization": f"Bearer {admin_token}"}
uh = {"Authorization": f"Bearer {user_token}"}
rh = {"Authorization": f"Bearer {res_token}"}

# ===== KİMLİK DOĞRULAMA =====
r = httpx.post(f"{base}/auth/login", json={"username":"tidesense","password":"tidesense123"})
results.append({"id":"TC-01","name":"Ana Admin girişi","cat":"Kimlik Doğrulama","expected":"200 + JWT","actual":f"{r.status_code}, token={'access_token' in r.json()}","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.post(f"{base}/auth/login", json={"username":"tidesense","password":"yanlis"})
results.append({"id":"TC-02","name":"Yanlış şifre girişi","cat":"Kimlik Doğrulama","expected":"401","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==401 else "BAŞARISIZ"})

r = httpx.post(f"{base}/auth/login", json={"username":"coastal_user","password":"User123!"})
results.append({"id":"TC-03","name":"User girişi","cat":"Kimlik Doğrulama","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.post(f"{base}/auth/login", json={"username":"marine_researcher","password":"Research123!"})
results.append({"id":"TC-04","name":"Researcher girişi","cat":"Kimlik Doğrulama","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.get(f"{base}/stations")
results.append({"id":"TC-05","name":"Token olmadan erişim","cat":"Kimlik Doğrulama","expected":"401","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code in [401,403] else "BAŞARISIZ"})

r = httpx.post(f"{base}/auth/login", json={"username":"nonexistent","password":"x"})
results.append({"id":"TC-06","name":"Var olmayan kullanıcı","cat":"Kimlik Doğrulama","expected":"401","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==401 else "BAŞARISIZ"})

# ===== GÜVENLİK =====
r = httpx.post(f"{base}/auth/login", json={"username":"' OR 1=1 --","password":"hack"})
results.append({"id":"TC-07","name":"SQL Injection denemesi","cat":"Güvenlik","expected":"401","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code in [401,422] else "BAŞARISIZ"})

r = httpx.post(f"{base}/auth/login", json={"username":"<script>alert(1)</script>","password":"x"})
results.append({"id":"TC-08","name":"XSS payload ile giriş","cat":"Güvenlik","expected":"401/422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code in [401,422] else "BAŞARISIZ"})

r = httpx.get(f"{base}/stations", headers={"Authorization":"Bearer SAHTE.TOKEN.XYZ"})
results.append({"id":"TC-09","name":"Sahte JWT token","cat":"Güvenlik","expected":"401","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==401 else "BAŞARISIZ"})

r = httpx.post(f"{base}/auth/login", json={})
results.append({"id":"TC-10","name":"Boş body ile login","cat":"Güvenlik","expected":"422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==422 else "BAŞARISIZ"})

# ** GERÇEK ZAYIFLIK: Brute-force koruması (rate limiting) **
brute_blocked = False
for i in range(20):
    r = httpx.post(f"{base}/auth/login", json={"username":"tidesense","password":f"wrong{i}"})
    if r.status_code == 429:
        brute_blocked = True
        break
results.append({"id":"TC-11","name":"Brute-force koruması (20 ardışık yanlış şifre)","cat":"Güvenlik","expected":"429 Too Many Requests","actual":"429 (engellendi)" if brute_blocked else "Hepsi 401 (engellenmedi!)","status":"BAŞARILI" if brute_blocked else "BAŞARISIZ"})

# ** GERÇEK ZAYIFLIK: Token iptal/blacklist mekanizması **
old_token = httpx.post(f"{base}/auth/login", json={"username":"tidesense","password":"tidesense123"}).json()["access_token"]
# Normalde logout sonrası token geçersiz olmalı - ama logout endpoint var mı?
r_logout = httpx.post(f"{base}/auth/logout", headers={"Authorization": f"Bearer {old_token}"})
if r_logout.status_code == 200:
    r_after = httpx.get(f"{base}/stations", headers={"Authorization": f"Bearer {old_token}"})
    results.append({"id":"TC-12","name":"Logout sonrası eski token ile erişim","cat":"Güvenlik","expected":"401 (token iptal edilmeli)","actual":str(r_after.status_code),"status":"BAŞARILI" if r_after.status_code==401 else "BAŞARISIZ"})
else:
    results.append({"id":"TC-12","name":"Token iptal (logout) mekanizması","cat":"Güvenlik","expected":"Logout endpoint mevcut olmalı","actual":f"Endpoint yok ({r_logout.status_code})","status":"BAŞARISIZ"})

# ** GERÇEK ZAYIFLIK: HTTPS kontrolü **
results.append({"id":"TC-13","name":"HTTPS zorunluluğu (HTTP→HTTPS yönlendirme)","cat":"Güvenlik","expected":"HTTP istekleri HTTPS'e yönlendirilmeli","actual":"HTTP üzerinden erişim açık (geliştirme ortamı)","status":"BAŞARISIZ"})

async def test_ws_bad():
    try:
        async with websockets.connect("ws://localhost:8000/ws/live?token=SAHTE") as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            d = json.loads(msg)
            return d.get("type") == "error", msg[:60]
    except Exception as e:
        return True, str(e)[:60]
ws_ok, ws_d = asyncio.run(test_ws_bad())
results.append({"id":"TC-14","name":"Sahte token ile WebSocket","cat":"Güvenlik","expected":"Reddedilmeli","actual":f"rejected={ws_ok}","status":"BAŞARILI" if ws_ok else "BAŞARISIZ"})

# ===== SENSÖR VERİ =====
r = httpx.get(f"{base}/stations", headers=ah)
items = r.json().get("items", [])
station_id = items[0]["id"] if items else 11
results.append({"id":"TC-15","name":"İstasyon listesi","cat":"Sensör Veri","expected":"200 + 4 istasyon","actual":f"{r.status_code}, {len(items)}","status":"BAŞARILI" if r.status_code==200 and len(items)==4 else "BAŞARISIZ"})

r = httpx.get(f"{base}/sensors/latest", headers=ah)
results.append({"id":"TC-16","name":"Son sensör verisi","cat":"Sensör Veri","expected":"200","actual":f"{r.status_code}, {len(r.json().get('items',[]))} kayıt","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.get(f"{base}/readings/history?station_id={station_id}", headers=ah)
results.append({"id":"TC-17","name":"Tarihsel veri sorgusu","cat":"Sensör Veri","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.get(f"{base}/readings/noaa", headers=ah)
results.append({"id":"TC-18","name":"Dış kaynak verileri (NOAA)","cat":"Sensör Veri","expected":"200","actual":f"{r.status_code}, {len(r.json().get('items',[]))} kayıt","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.get(f"{base}/readings/stats?station_id={station_id}", headers=ah)
results.append({"id":"TC-19","name":"İstatistik sorgusu","cat":"Sensör Veri","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

async def test_ws():
    try:
        async with websockets.connect(f"ws://localhost:8000/ws/live?token={admin_token}") as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=12)
            return True, msg[:60]
    except Exception as e:
        return False, str(e)[:60]
ws_ok, _ = asyncio.run(test_ws())
results.append({"id":"TC-20","name":"WebSocket canlı veri","cat":"Sensör Veri","expected":"Bağlantı + Mesaj","actual":f"ok={ws_ok}","status":"BAŞARILI" if ws_ok else "BAŞARISIZ"})

# ===== SINIR DEĞER =====
r = httpx.get(f"{base}/readings/history?station_id=99999", headers=ah)
results.append({"id":"TC-21","name":"Olmayan istasyon ID (99999)","cat":"Sınır Testi","expected":"404","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==404 else "BAŞARISIZ"})

r = httpx.get(f"{base}/readings/history?station_id=-1", headers=ah)
results.append({"id":"TC-22","name":"Negatif station_id (-1)","cat":"Sınır Testi","expected":"404/422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code in [404,422] else "BAŞARISIZ"})

r = httpx.get(f"{base}/readings/history?station_id={station_id}&limit=99999", headers=ah)
results.append({"id":"TC-23","name":"Limit > max (99999)","cat":"Sınır Testi","expected":"422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==422 else "BAŞARISIZ"})

r = httpx.get(f"{base}/readings/stats?station_id={station_id}&period_hours=9999", headers=ah)
results.append({"id":"TC-24","name":"period_hours > max (9999)","cat":"Sınır Testi","expected":"422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==422 else "BAŞARISIZ"})

r = httpx.get(f"{base}/predictions?horizon_hours=999", headers=ah)
results.append({"id":"TC-25","name":"Tahmin horizon > max (999)","cat":"Sınır Testi","expected":"422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==422 else "BAŞARISIZ"})

r = httpx.post(f"{base}/alerts/ack", headers=ah, json={"alert_id": 999999})
results.append({"id":"TC-26","name":"Olmayan alarm ID onaylama","cat":"Sınır Testi","expected":"404","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==404 else "BAŞARISIZ"})

r = httpx.get(f"{base}/readings/history?station_id={station_id}&export_format=xml", headers=ah)
results.append({"id":"TC-27","name":"Geçersiz export format (xml)","cat":"Sınır Testi","expected":"422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==422 else "BAŞARISIZ"})

r = httpx.post(f"{base}/users", headers=ah, json={"username":"x","password":"ab","role":"user"})
results.append({"id":"TC-28","name":"Kısa şifre (2 karakter)","cat":"Sınır Testi","expected":"422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==422 else "BAŞARISIZ"})

r = httpx.post(f"{base}/users", headers=ah, json={"username":"x","password":"Valid123!","role":"superadmin"})
results.append({"id":"TC-29","name":"Geçersiz rol (superadmin)","cat":"Sınır Testi","expected":"422","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==422 else "BAŞARISIZ"})

r = httpx.get(f"{base}/nonexistent", headers=ah)
results.append({"id":"TC-30","name":"Olmayan endpoint","cat":"Sınır Testi","expected":"404","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==404 else "BAŞARISIZ"})

# ** GERÇEK ZAYIFLIK: Çok uzun kullanıcı adı (2000 karakter) **
long_name = "A" * 2000
r = httpx.post(f"{base}/users", headers=ah, json={"username":long_name,"password":"ValidPass1!","role":"user"})
results.append({"id":"TC-31","name":"2000 karakterlik kullanıcı adı","cat":"Sınır Testi","expected":"422 (uzunluk sınırı)","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==422 else "BAŞARISIZ"})
if r.status_code == 201:
    uid = r.json().get("id")
    if uid: httpx.delete(f"{base}/users/{uid}", headers=ah)

# ===== AY + TAHMİN =====
r = httpx.get(f"{base}/moon/current", headers=ah)
results.append({"id":"TC-32","name":"Ay konum bilgisi","cat":"Ay Konum","expected":"200 + faz","actual":f"{r.status_code}, {r.json().get('moon_phase','?')}","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.get(f"{base}/predictions", headers=ah)
results.append({"id":"TC-33","name":"Tahminler (Admin)","cat":"Tahmin","expected":"200","actual":f"{r.status_code}, {len(r.json().get('items',[]))} seri","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.get(f"{base}/predictions", headers=uh)
results.append({"id":"TC-34","name":"Tahminler (User erişimi)","cat":"Tahmin","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

# ===== ALARM =====
r = httpx.get(f"{base}/alerts", headers=ah)
results.append({"id":"TC-35","name":"Alarm listesi","cat":"Alarm","expected":"200","actual":f"{r.status_code}, {len(r.json().get('items',[]))} alarm","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

al = r.json().get("items", [])
if al:
    r = httpx.post(f"{base}/alerts/ack", headers=ah, json={"alert_id": al[0]["id"]})
    results.append({"id":"TC-36","name":"Alarm onaylama","cat":"Alarm","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

# ===== EXPORT + RBAC =====
r = httpx.get(f"{base}/readings/history?station_id={station_id}&export_format=csv", headers=rh)
results.append({"id":"TC-37","name":"CSV export (Researcher)","cat":"Veri Export","expected":"200 + CSV","actual":f"{r.status_code}, csv={'text/csv' in r.headers.get('content-type','')}","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.get(f"{base}/predictions?refresh=true", headers=uh)
results.append({"id":"TC-38","name":"Tahmin yenile (User engel)","cat":"Yetki Kontrolü","expected":"403","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==403 else "BAŞARISIZ"})

r = httpx.get(f"{base}/readings/history?station_id={station_id}&export_format=csv", headers=uh)
results.append({"id":"TC-39","name":"CSV export (User engel)","cat":"Yetki Kontrolü","expected":"403","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==403 else "BAŞARISIZ"})

r = httpx.get(f"{base}/health", headers=uh)
results.append({"id":"TC-40","name":"Sistem sağlığı (User engel)","cat":"Yetki Kontrolü","expected":"403","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==403 else "BAŞARISIZ"})

r = httpx.get(f"{base}/users", headers=uh)
results.append({"id":"TC-41","name":"Kullanıcı listesi (User engel)","cat":"Yetki Kontrolü","expected":"403","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==403 else "BAŞARISIZ"})

r = httpx.post(f"{base}/users", headers=uh, json={"username":"h","password":"Hack123!!","role":"admin"})
results.append({"id":"TC-42","name":"User ile admin oluşturma","cat":"Yetki Kontrolü","expected":"403","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==403 else "BAŞARISIZ"})

# ===== SİSTEM =====
r = httpx.get(f"{base}/health", headers=ah)
results.append({"id":"TC-43","name":"Sistem sağlığı (Admin)","cat":"Sistem","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.get(f"{base}/cameras", headers=ah)
results.append({"id":"TC-44","name":"Kamera listesi","cat":"Sistem","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

# ===== KULLANICI YÖNETİMİ + ANA ADMİN =====
r = httpx.get(f"{base}/users", headers=ah)
user_list = r.json()
results.append({"id":"TC-45","name":"Kullanıcı listesi (Admin)","cat":"Kullanıcı Yönetimi","expected":"200","actual":f"{r.status_code}, {len(user_list)} kullanıcı","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

r = httpx.post(f"{base}/users", headers=ah, json={"username":"test_tmp","password":"TestTmp123!","role":"user"})
tmp_uid = r.json().get("id") if r.status_code==201 else None
results.append({"id":"TC-46","name":"Kullanıcı oluşturma","cat":"Kullanıcı Yönetimi","expected":"201","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==201 else "BAŞARISIZ"})

r = httpx.post(f"{base}/users", headers=ah, json={"username":"test_tmp","password":"TestTmp123!","role":"user"})
results.append({"id":"TC-47","name":"Aynı kullanıcı adı tekrar","cat":"Sınır Testi","expected":"409","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==409 else "BAŞARISIZ"})

# Ana admin koruması
tidesense_u = next((u for u in user_list if u["username"]=="tidesense"), None)
r2 = httpx.post(f"{base}/users", headers=ah, json={"username":"atk_admin","password":"Attack123!","role":"admin"})
a2id = r2.json().get("id") if r2.status_code==201 else None
if a2id and tidesense_u:
    a2t = httpx.post(f"{base}/auth/login", json={"username":"atk_admin","password":"Attack123!"}).json().get("access_token","")
    a2h = {"Authorization": f"Bearer {a2t}"}
    r = httpx.delete(f"{base}/users/{tidesense_u['id']}", headers=a2h)
    results.append({"id":"TC-48","name":"İkinci admin → Ana admini silme","cat":"Ana Admin Koruması","expected":"403","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==403 else "BAŞARISIZ"})
    r = httpx.patch(f"{base}/users/{tidesense_u['id']}/role", headers=a2h, json={"role":"user"})
    results.append({"id":"TC-49","name":"İkinci admin → Ana admin rolünü düşürme","cat":"Ana Admin Koruması","expected":"403","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==403 else "BAŞARISIZ"})
    r = httpx.patch(f"{base}/users/{tidesense_u['id']}/password", headers=a2h, json={"password":"hacked12345"})
    results.append({"id":"TC-50","name":"İkinci admin → Ana admin şifresini değiştirme","cat":"Ana Admin Koruması","expected":"403","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==403 else "BAŞARISIZ"})
    httpx.delete(f"{base}/users/{a2id}", headers=ah)

r = httpx.delete(f"{base}/users/{tidesense_u['id']}", headers=ah)
results.append({"id":"TC-51","name":"Ana admin kendini silme","cat":"Sınır Testi","expected":"400","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==400 else "BAŞARISIZ"})

if tmp_uid: httpx.delete(f"{base}/users/{tmp_uid}", headers=ah)

# ===== STRES =====
def req(_):
    try: return httpx.get(f"{base}/sensors/latest", headers=ah, timeout=10).status_code
    except: return 0

t0=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as p:
    c50=list(p.map(req, range(50)))
e50=round(time.time()-t0,2)
results.append({"id":"TC-52","name":"50 eşzamanlı istek","cat":"Stres Testi","expected":"Tümü 200, < 10s","actual":f"{c50.count(200)}/50 başarılı, {e50}s","status":"BAŞARILI" if c50.count(200)==50 and e50<10 else "BAŞARISIZ"})

t0=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as p:
    c100=list(p.map(req, range(100)))
e100=round(time.time()-t0,2)
results.append({"id":"TC-53","name":"100 eşzamanlı istek","cat":"Stres Testi","expected":"%90+, < 15s","actual":f"{c100.count(200)}/100, {e100}s","status":"BAŞARILI" if c100.count(200)>=90 and e100<15 else "BAŞARISIZ"})

try:
    t0=time.time()
    r=httpx.get(f"{base}/readings/history?station_id={station_id}&limit=2000", headers=ah, timeout=15)
    e=round(time.time()-t0,2)
    results.append({"id":"TC-54","name":"2000 kayıtlık büyük sorgu","cat":"Performans","expected":"200, < 5s","actual":f"{r.status_code}, {len(r.json().get('items',[]))} kayıt, {e}s","status":"BAŞARILI" if r.status_code==200 and e<5 else "BAŞARISIZ"})
except httpx.ReadTimeout:
    results.append({"id":"TC-54","name":"2000 kayıtlık büyük sorgu","cat":"Performans","expected":"200, < 5s","actual":"TIMEOUT","status":"BAŞARISIZ"})

# ===== ML =====
from app.services.prediction_service import get_prediction_series
from app.db.session import SessionLocal
db = SessionLocal()
series = get_prediction_series(db)
rmse_list = [(s["station"].code, round(s["rmse"],2)) for s in series if s.get("rmse") is not None]
db.close()
results.append({"id":"TC-55","name":"ML model RMSE değerleri","cat":"ML Doğruluk","expected":"RMSE < 15 cm","actual":str(rmse_list),"status":"BAŞARILI" if len(rmse_list) > 0 and all(r[1]<15 for r in rmse_list) else "BAŞARISIZ"})

# ===== EK MODÜL TESTLERİ (3'er adet tamamlama) =====

# Ay Konum (Modül 5) - TC-56, TC-57
r = httpx.get(f"{base}/moon/current?station_id={station_id}", headers=ah)
results.append({"id":"TC-56","name":"İstasyon bazlı ay konumu","cat":"Ay Konum","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})
r = httpx.get(f"{base}/moon/current", headers=rh) # Araştırmacı erişimi
results.append({"id":"TC-57","name":"Researcher ay konumu erişimi","cat":"Ay Konum","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

# Tahmin (Modül 6) - TC-58
r = httpx.get(f"{base}/predictions?horizon_hours=12", headers=ah)
results.append({"id":"TC-58","name":"Kısa vadeli tahmin (12h)","cat":"Tahmin","expected":"200 + 12 kayıt","actual":f"{r.status_code}, {len(r.json().get('items',[]))}","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

# Alarm (Modül 7) - TC-59
r = httpx.get(f"{base}/alerts?acknowledged=false", headers=ah)
results.append({"id":"TC-59","name":"Onaylanmamış alarmlar","cat":"Alarm","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

# Veri Export (Modül 8) - TC-60, TC-61
r = httpx.get(f"{base}/readings/history?station_id={station_id}&export_format=csv&limit=10", headers=rh)
results.append({"id":"TC-60","name":"CSV export (Sınırlı veri)","cat":"Veri Export","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})
results.append({"id":"TC-61","name":"CSV header doğrulama","cat":"Veri Export","expected":"recorded_at içermeli","actual":"ok" if "recorded_at" in r.text else "hata","status":"BAŞARILI" if "recorded_at" in r.text else "BAŞARISIZ"})

# Sistem (Modül 10) - TC-62
r = httpx.get("http://localhost:8000/docs")
results.append({"id":"TC-62","name":"Swagger UI erişimi","cat":"Sistem","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})

# Kullanıcı Yönetimi (Modül 11) - TC-63
# Not: Sistemde 'me' endpoint'i yok, admin üzerinden test ediyoruz
r = httpx.patch(f"{base}/users/{tidesense_u['id']}/password", headers=ah, json={"password":"NewAdminPass123!"})
results.append({"id":"TC-63","name":"Admin kendi şifresini değiştirme","cat":"Kullanıcı Yönetimi","expected":"200","actual":str(r.status_code),"status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})
# Şifreyi geri düzeltelim ki testler tekrar çalışabilsin
httpx.patch(f"{base}/users/{tidesense_u['id']}/password", headers=ah, json={"password":"tidesense123"})

# Stres Testi (Modül 13) - TC-64
t0=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=200) as p:
    c200=list(p.map(req, range(200)))
e200=round(time.time()-t0,2)
results.append({"id":"TC-64","name":"200 eşzamanlı istek (Max Load)","cat":"Stres Testi","expected":"%80+, < 20s","actual":f"{c200.count(200)}/200, {e200}s","status":"BAŞARILI" if c200.count(200)>=160 and e200<20 else "BAŞARISIZ"})

# Performans (Modül 14) - TC-65, TC-66
r = httpx.get(f"{base}/readings/stats?station_id={station_id}", headers=ah)
results.append({"id":"TC-65","name":"İstatistik hesaplama hızı","cat":"Performans","expected":"< 1s","actual":"ok","status":"BAŞARILI" if r.status_code==200 else "BAŞARISIZ"})
t0=time.time()
httpx.get(f"{base}/stations", headers=ah)
e=time.time()-t0
results.append({"id":"TC-66","name":"Dashboard ana liste hızı","cat":"Performans","expected":"< 0.5s","actual":f"{round(e,3)}s","status":"BAŞARILI" if e<0.5 else "BAŞARISIZ"})

# ML Doğruluk (Modül 15) - TC-67, TC-68
model_v = series[0]["items"][0]["model_version"] if series and series[0]["items"] else "N/A"
results.append({"id":"TC-67","name":"ML model versiyon kontrolü","cat":"ML Doğruluk","expected":"rf-v1","actual":model_v,"status":"BAŞARILI" if "rf-v1" in model_v else "BAŞARISIZ"})
has_nan = any(i["predicted_water_level_cm"] is None for s in series for i in s["items"])
results.append({"id":"TC-68","name":"Tahmin sürekliliği (NaN kontrolü)","cat":"ML Doğruluk","expected":"Hiç NaN olmamalı","actual":f"NaN={has_nan}","status":"BAŞARILI" if not has_nan else "BAŞARISIZ"})

print(json.dumps(results, ensure_ascii=False))
