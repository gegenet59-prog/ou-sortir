# Télécharge tous les restaurants et fast-foods de la métropole lilloise (OpenStreetMap)
# et les range dans data/restos-lille.json, en format compact pour l'onglet « Manger ».
import json, os, sys, time, urllib.request, urllib.parse

ZONE = (50.52, 2.80, 50.82, 3.30)   # sud, ouest, nord, est : Métropole Européenne de Lille
REQUETE = f"""[out:json][timeout:180];
nwr["amenity"~"^(restaurant|fast_food)$"]({ZONE[0]},{ZONE[1]},{ZONE[2]},{ZONE[3]});
out center tags;"""
SERVEURS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"]

def telecharger():
    for essai in range(4):
        for s in SERVEURS:
            try:
                req = urllib.request.Request(s, data=urllib.parse.urlencode({"data": REQUETE}).encode(),
                                             headers={"User-Agent": "ou-sortir (GitHub Actions)"})
                with urllib.request.urlopen(req, timeout=240) as r:
                    return json.load(r)["elements"]
            except Exception as e:
                print("Échec", s, e, flush=True)
        time.sleep(30)
    sys.exit("Aucun serveur OpenStreetMap n'a répondu")

def lien(u):
    u = (u or "").split(";")[0].strip()
    if u and not u.startswith("http"): u = "https://" + u
    return u if "." in u else ""

lieux, vus = [], set()
for e in telecharger():
    t = e.get("tags", {}); la = e.get("lat") or e.get("center", {}).get("lat"); lo = e.get("lon") or e.get("center", {}).get("lon")
    if la is None or not t.get("name"): continue
    cle = (t["name"].lower(), round(la, 3), round(lo, 3))
    if cle in vus: continue
    vus.add(cle)
    adresse = ", ".join(x for x in [" ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x), t.get("addr:city")] if x)
    cuisine = (t.get("cuisine") or "").split(";")[0].strip().lower()
    lieux.append([t["name"], round(la, 6), round(lo, 6), t["amenity"], adresse, t.get("opening_hours", ""),
                  t.get("phone") or t.get("contact:phone", ""),
                  lien(t.get("website") or t.get("contact:website") or t.get("url") or t.get("contact:instagram") or t.get("contact:facebook")),
                  cuisine])

if len(lieux) < 300: sys.exit(f"Seulement {len(lieux)} restos : résultat suspect, on garde l'ancienne liste")
os.makedirs("data", exist_ok=True)
json.dump({"zone": ZONE, "maj": time.strftime("%Y-%m-%d"), "lieux": lieux}, open("data/restos-lille.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(lieux), "restos enregistrés,", sum(l[3] == "fast_food" for l in lieux), "fast-foods,", sum(bool(l[5]) for l in lieux), "avec horaires")
