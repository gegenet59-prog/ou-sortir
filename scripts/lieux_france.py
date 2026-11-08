# Télécharge tous les bars, pubs et clubs de France (OpenStreetMap), puis les range
# en petits carrés (« tuiles ») : le téléphone ne charge que le coin où l'on se trouve.
import json, math, os, shutil, sys, time, urllib.request, urllib.parse

PAS = 0.25   # taille d'un carré en degrés (~28 km x 18 km)
REQUETE = """[out:json][timeout:900][maxsize:1073741824];
area["ISO3166-1"="FR"][admin_level=2]->.fr;
nwr["amenity"~"^(bar|pub|biergarten|nightclub)$"](area.fr);
out center tags;"""
SERVEURS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"]

def telecharger():
    for essai in range(3):
        for s in SERVEURS:
            try:
                print("Essai", s, flush=True)
                req = urllib.request.Request(s, data=urllib.parse.urlencode({"data": REQUETE}).encode(),
                                             headers={"User-Agent": "ou-sortir (GitHub Actions)"})
                with urllib.request.urlopen(req, timeout=1000) as r:
                    return json.load(r)["elements"]
            except Exception as e:
                print("Échec", s, e, flush=True)
        time.sleep(60)
    sys.exit("Aucun serveur OpenStreetMap n'a répondu")

def lien(u):
    u = (u or "").split(";")[0].strip()
    if u and not u.startswith("http"): u = "https://" + u
    return u if "." in u else ""

tuiles, vus, total = {}, set(), 0
for e in telecharger():
    t = e.get("tags", {}); la = e.get("lat") or e.get("center", {}).get("lat"); lo = e.get("lon") or e.get("center", {}).get("lon")
    if la is None or not t.get("name"): continue
    cle = (t["name"].lower(), round(la, 3), round(lo, 3))
    if cle in vus: continue
    vus.add(cle)
    adresse = ", ".join(x for x in [" ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x), t.get("addr:city")] if x)
    lieu = [t["name"], round(la, 6), round(lo, 6), t["amenity"], adresse, t.get("opening_hours", ""),
            t.get("phone") or t.get("contact:phone", ""),
            lien(t.get("website") or t.get("contact:website") or t.get("url") or t.get("contact:instagram") or t.get("contact:facebook"))]
    tuiles.setdefault(f"{math.floor(la / PAS)}_{math.floor(lo / PAS)}", []).append(lieu)
    total += 1

if total < 5000: sys.exit(f"Seulement {total} lieux : résultat suspect, on garde l'ancienne liste")
shutil.rmtree("data", ignore_errors=True); os.makedirs("data/tuiles")
for k, l in tuiles.items():
    json.dump(l, open(f"data/tuiles/{k}.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump({"pas": PAS, "maj": time.strftime("%Y-%m-%d"), "total": total, "tuiles": sorted(tuiles)},
          open("data/index.json", "w"), separators=(",", ":"))
taille = sum(os.path.getsize(f"data/tuiles/{k}.json") for k in tuiles)
print(f"{total} lieux enregistrés dans {len(tuiles)} carrés ({taille // 1024} Ko),",
      sum(l[3] == "nightclub" for v in tuiles.values() for l in v), "clubs,",
      sum(bool(l[5]) for v in tuiles.values() for l in v), "avec horaires")
