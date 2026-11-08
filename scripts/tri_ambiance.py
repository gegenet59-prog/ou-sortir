# Classe chaque lieu : "club", "disco", "dansant", "ambiance", "autre" (bar sans indice d'ambiance, masqué par défaut)
# ou None (bar-tabac / PMU → retiré).
# Utilisé par lieux_france.py (avec toutes les étiquettes OSM) et pour retrier une liste existante (nom + horaires).
import re

TABAC = re.compile(r"\b(tabac|pmu|fdj|loto|presse|fran[cç]aise des jeux|bar[- ]tabac|civette)\b", re.I)
DANSANT = re.compile(r"\b(dancing|dansant|danse|dance|salsa|latino|latin|bachata|karaok[eé]|disco|guinguette|cabaret|bal)\b", re.I)
DISCO = re.compile(r"\b(discoth[eè]que|disco)\b", re.I)
AMBIANCE = re.compile(r"\b(lounge|cocktails?|rooftop|speakeasy|club|night|nuit|after|shots?|rhum|rum|tiki|mojito|tapas|beer|bi[eè]re|brew|brasseur|tap|taproom|irish|pub|biergarten|jazz|rock|live|music|musique|sound|vinyl|dj|gay|queer|lgbt|electro|techno|house|wine bar)\b", re.I)

def ferme_tard(oh):
    """Vrai si une plage horaire se termine après 1h du matin."""
    for deb, fin in re.findall(r"(\d{1,2}):\d{2}\s*-\s*(\d{1,2}):\d{2}", oh or ""):
        deb, fin = int(deb), int(fin)
        if fin >= 25 or (fin < deb and fin >= 1): return True
    return False

def categorie(nom, type_, horaires, tags=None):
    t = tags or {}
    if type_ == "nightclub":
        return "disco" if DISCO.search(nom) else "club"
    if TABAC.search(nom) or t.get("shop") in ("tobacco", "kiosk", "newsagent") or t.get("tobacco") == "yes" \
       or t.get("lottery") == "yes" or t.get("gambling") or t.get("betting") == "yes":
        return None
    if DANSANT.search(nom) or t.get("dance:teaching") or t.get("dancing") == "yes" or t.get("dance") == "yes" or t.get("karaoke") == "yes":
        return "dansant"
    if type_ in ("pub", "biergarten") or ferme_tard(horaires) or AMBIANCE.search(nom) \
       or t.get("live_music") == "yes" or t.get("music") or t.get("cocktails") == "yes" or t.get("drink:cocktail") in ("yes", "served") \
       or t.get("bar") in ("cocktail", "lounge", "music") or t.get("lgbtq") in ("primary", "welcome", "only"):
        return "ambiance"
    return "autre"

if __name__ == "__main__":   # retrie les carrés déjà téléchargés (sans les étiquettes OSM)
    import json, glob, os
    gardes = retires = 0; tuiles = []
    for f in glob.glob("data/tuiles/*.json"):
        l = json.load(open(f)); nouv = []
        for x in l:
            c = categorie(x[0], x[3], x[5])
            if c: nouv.append(x[:8] + [c]); gardes += 1
            else: retires += 1
        if nouv: json.dump(nouv, open(f, "w"), ensure_ascii=False, separators=(",", ":")); tuiles.append(os.path.basename(f)[:-5])
        else: os.remove(f)
    i = json.load(open("data/index.json")); i.update(total=gardes, tuiles=sorted(tuiles)); json.dump(i, open("data/index.json", "w"), separators=(",", ":"))
    print(gardes, "gardés,", retires, "retirés (tabac/PMU)")
