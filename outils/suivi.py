"""Suivi des performances de NOS vidéos publiées : saisie manuelle, comparaisons prudentes, rapport, apprentissage.

Données : suivi/stats.csv (une ligne = un relevé des statistiques d'une publication à une date). S'ouvre dans Excel
(séparateur « ; », virgule décimale acceptée). Cellule vide = donnée absente : elle reste nulle, jamais estimée.
Le reste (concept, moteur, mécaniques, hook, fin, format) est lu dans le projet : aucune double saisie.

Usage :
  python3 outils/suivi.py ajouter <projet> [epNNN] --publie AAAA-MM-JJ [--releve AAAA-MM-JJ] [--plateforme tiktok]
          [--vues N] [--likes N] [--commentaires N] [--partages N] [--favoris N] [--temps-moyen S] [--completion PCT]
          [--abonnes N] [--revenus EUR] [--duree S] [--compte NOM] [--url URL] [--test ID --variante TEXTE] [--notes TXT]
  python3 outils/suivi.py verifier                 contrôle stats.csv (code 1 si erreur)
  python3 outils/suivi.py liste                    une ligne par publication (dernier relevé)
  python3 outils/suivi.py comparer <pubA> <pubB>   deux publications côte à côte, au même âge si possible
  python3 outils/suivi.py rapport [--age 7] [--sans-apprentissage]
          → suivi/rapports/AAAA-MM-JJ.md + bloc calculé « resultats_propres » de chaque mécanique (bible/mecaniques.json)

Principes :
- Comparer au même âge : des vues à J+2 et à J+30 ne se comparent pas. Le rapport prend, pour chaque publication,
  le relevé le plus proche de J+age (tolérance ± moitié de l'âge) et exclut les autres en le disant.
- Vues relatives : vues ÷ médiane des autres publications du même compte au même âge (neutralise la taille du compte).
- Observationnel : un écart est une corrélation. Le rapport liste les variables confondues (même hook, même projet,
  même moteur…) et ne parle jamais de cause. Une vidéo ou un seul projet = hypothèse. Causalité : seulement par
  test A/B (même épisode publié en deux variantes, colonnes test + variante).
- Apprentissage : écrit seulement le bloc calculé « resultats_propres » de bible/mecaniques.json. Ne touche jamais
  aux champs écrits à la main, aux preuves du corpus, à bible/controles.json, aux recettes ni à CLAUDE.md.
"""
import argparse
import csv
import datetime as dt
import io
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import BIBLE, PROJETS, STUDIO, ecrire_json, lire_json  # noqa: E402

SUIVI = STUDIO / "suivi"
STATS = SUIVI / "stats.csv"
RAPPORTS = SUIVI / "rapports"
REGISTRE = BIBLE / "mecaniques.json"

COLONNES = ["projet", "episode", "plateforme", "compte", "date_publication", "date_releve", "vues", "likes",
            "commentaires", "partages", "favoris", "temps_moyen_s", "completion_pct", "nouveaux_abonnes",
            "revenus_eur", "duree_s", "url", "test", "variante", "notes"]
ENTIERS = ("vues", "likes", "commentaires", "partages", "favoris", "nouveaux_abonnes")
DECIMAUX = ("temps_moyen_s", "completion_pct", "revenus_eur", "duree_s")
METRIQUES = {  # id : (libellé, format)
    "indice_vues": ("vues relatives au compte", "x"),
    "vues": ("vues", "n"),
    "taux_commentaires": ("commentaires / 1 000 vues", "d"),
    "taux_likes": ("likes / 1 000 vues", "d"),
    "taux_partages": ("partages / 1 000 vues", "d"),
    "taux_favoris": ("favoris / 1 000 vues", "d"),
    "abonnes_1000": ("abonnés / 1 000 vues", "d"),
    "completion_pct": ("taux de complétion (%)", "d"),
    "part_regardee": ("temps moyen / durée (%)", "d"),
    "revenus_1000": ("revenus / 1 000 vues (€)", "d"),
}
DIMENSIONS = {  # id : libellé (une valeur par publication, sauf mecanique)
    "accroche": "type de hook", "fin": "type de fin", "moteur": "moteur narratif (concept)", "format": "format",
    "rang": "place dans la série", "duree": "tranche de durée", "projet": "projet", "verdict": "verdict du Script Doctor",
}
MIEUX, MOINS = 1.25, 0.8   # écart net (même convention que la bibliothèque des mécaniques)


class ErreurSaisie(ValueError):
    pass


# ====================================================================== lecture / écriture du CSV
def _nombre(txt, col, entier):
    """'12 300' → 12300 ; '12,5' → 12.5 ; '0:14' → 14 (temps) ; '45 %' → 45 ; '' → None. Refuse les arrondis 12K."""
    s = str(txt or "").strip().replace(" ", "").replace("\xa0", "").replace(" ", "").replace("€", "").replace("%", "")
    if s in ("", "-", "—", "na", "n/a", "nd"):
        return None
    if re.fullmatch(r"[\d.,]+[kKmM]", s):
        raise ErreurSaisie(f"{col} = {txt} : valeur arrondie. Saisir le chiffre exact de TikTok Studio (ou laisser vide).")
    if col == "temps_moyen_s" and ":" in s:
        m, _, sec = s.partition(":")
        return int(m) * 60 + float(sec.replace(",", "."))
    if entier:
        if not re.fullmatch(r"\d+", s.replace(".", "").replace(",", "")) or re.search(r"[.,]\d{1,2}$", s):
            raise ErreurSaisie(f"{col} = {txt} : nombre entier attendu")
        return int(s.replace(".", "").replace(",", ""))
    try:
        return float(s.replace(",", "."))
    except ValueError:
        raise ErreurSaisie(f"{col} = {txt} : nombre attendu") from None


def _date(txt, col):
    s = str(txt or "").strip()
    if not s:
        return None
    for f in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(s, f).date()
        except ValueError:
            continue
    raise ErreurSaisie(f"{col} = {txt} : date AAAA-MM-JJ (ou JJ/MM/AAAA) attendue")


def lire_csv(chemin=None):
    """[(n° de ligne, dict brut)] ; accepte UTF-8 (avec ou sans BOM) et l'encodage d'Excel Windows."""
    f = Path(chemin or STATS)
    if not f.exists():
        return []
    brut = f.read_bytes()
    try:
        texte = brut.decode("utf-8-sig")
    except UnicodeDecodeError:
        texte = brut.decode("cp1252")
    premiere = texte.splitlines()[0] if texte.strip() else ""
    sep = ";" if premiere.count(";") >= premiere.count(",") else ","
    lecteur = csv.DictReader(io.StringIO(texte), delimiter=sep)
    return [(i + 2, {k.strip(): (v or "").strip() for k, v in r.items() if k}) for i, r in enumerate(lecteur)
            if any((v or "").strip() for v in r.values())]


def ecrire_ligne(ligne, chemin=None):
    f = Path(chemin or STATS)
    f.parent.mkdir(parents=True, exist_ok=True)
    neuf = not f.exists() or not f.read_text(encoding="utf-8-sig").strip()
    with open(f, "a", encoding="utf-8-sig" if neuf else "utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=COLONNES, delimiter=";")
        if neuf:
            w.writeheader()
        w.writerow({k: ("" if ligne.get(k) is None else str(ligne[k]).replace(".", ",") if isinstance(ligne.get(k), float)
                        else ligne[k]) for k in COLONNES})


# ====================================================================== publications enrichies par le projet
def pub_id(projet, episode, plateforme, variante=""):
    return f"{projet}/{episode}/{plateforme}" + (f"#{variante}" if variante else "")


def tranche(d):
    if d is None:
        return None
    for borne, nom in ((45, "< 45 s"), (60, "45-60 s"), (75, "60-75 s"), (90, "75-90 s")):
        if d < borne:
            return nom
    return "90 s et +"


def duree_montee(dos):
    """Durée mesurée par /monter (rapport.md), sinon None : jamais la durée des rushs."""
    f = dos / "rapport.md"
    if f.exists():
        m = re.search(r"Durée[^|]*\|\s*([\d.]+)\s*s", f.read_text(encoding="utf-8"))
        if m:
            return float(m.group(1))
    return None


def caracteristiques(projet, episode, projets=None):
    """Ce que le projet dit de la vidéo. Absent = None (jamais deviné)."""
    racine = Path(projets or PROJETS) / projet
    pj = lire_json(racine / "projet.json")
    dos = racine / "episodes" / episode
    ep = lire_json(dos / "episode.json")
    rv = lire_json(dos / "revue.json") if (dos / "revue.json").exists() else {}
    serie = pj.get("type") == "serie"
    num = ep.get("numero", 1)
    return {
        "titre": ep.get("titre") or pj.get("titre"), "concept": pj.get("concept") or pj.get("sujet"),
        "moteur": pj.get("moteur_narratif"), "domaine": pj.get("domaine"),
        "accroche": ep.get("accroche_type"), "fin": ep.get("cliff_type"), "format": ep.get("format"),
        "rang": ("partie 1" if num == 1 else "suite") if serie else "vidéo unique",
        "mecaniques": ep.get("mecaniques_utilisees"),  # None = non renseignées (≠ aucune)
        "verdict": rv.get("verdict"), "duree_montee": duree_montee(dos),
        "hooks_alternatifs": ep.get("hooks_alternatifs", []),
    }


def charger(chemin=None, projets=None):
    """(publications, erreurs). Publication = métadonnées + caractéristiques + relevés triés par date."""
    pubs, erreurs = {}, []
    for n, r in lire_csv(chemin):
        try:
            for k in ("projet", "date_publication", "date_releve"):
                if not r.get(k):
                    raise ErreurSaisie(f"{k} obligatoire")
            ep = r.get("episode") or "ep001"
            if not (Path(projets or PROJETS) / r["projet"] / "episodes" / ep / "episode.json").exists():
                raise ErreurSaisie(f"épisode inconnu : projets/{r['projet']}/episodes/{ep}")
            plat = (r.get("plateforme") or "tiktok").lower()
            dp, dr = _date(r["date_publication"], "date_publication"), _date(r["date_releve"], "date_releve")
            if dr < dp:
                raise ErreurSaisie("date_releve avant date_publication")
            rel = {"date": dr, "age": (dr - dp).days}
            for c in ENTIERS:
                rel[c] = _nombre(r.get(c), c, True)
            for c in DECIMAUX:
                rel[c] = _nombre(r.get(c), c, False)
            if rel["completion_pct"] is not None and not 0 <= rel["completion_pct"] <= 100:
                raise ErreurSaisie(f"completion_pct = {rel['completion_pct']} : pourcentage de 0 à 100")
            for c in ("likes", "commentaires", "partages", "favoris", "nouveaux_abonnes"):
                if rel[c] is not None and rel["vues"] is not None and rel[c] > rel["vues"]:
                    raise ErreurSaisie(f"{c} ({rel[c]}) > vues ({rel['vues']}) : colonnes inversées ?")
            pid = pub_id(r["projet"], ep, plat, r.get("variante", ""))
            if pid not in pubs:
                carac = caracteristiques(r["projet"], ep, projets)
                pubs[pid] = {"id": pid, "projet": r["projet"], "episode": ep, "plateforme": plat,
                             "compte": r.get("compte") or "principal", "date_publication": dp, "url": r.get("url") or None,
                             "test": r.get("test") or None, "variante": r.get("variante") or None,
                             "duree_s": None, "releves": [], **carac}
            p = pubs[pid]
            if p["date_publication"] != dp:
                raise ErreurSaisie(f"{pid} : date_publication différente d'une ligne précédente ({p['date_publication']})")
            if rel["duree_s"] is not None:
                p["duree_s"] = rel["duree_s"]
            if any(x["date"] == dr for x in p["releves"]):
                raise ErreurSaisie(f"{pid} : deux relevés le {dr}")
            p["releves"].append(rel)
        except ErreurSaisie as e:
            erreurs.append(f"ligne {n} : {e}")
        except (OSError, ValueError, KeyError) as e:
            erreurs.append(f"ligne {n} : {type(e).__name__} {e}")
    for p in pubs.values():
        p["releves"].sort(key=lambda x: x["date"])
        if p["duree_s"] is None:
            p["duree_s"] = p["duree_montee"]
        p["tranche"] = tranche(p["duree_s"])
        for rel in p["releves"]:
            if rel["temps_moyen_s"] is not None and p["duree_s"] and rel["temps_moyen_s"] > p["duree_s"] * 1.5:
                erreurs.append(f"{p['id']} : temps moyen {rel['temps_moyen_s']} s > durée {p['duree_s']} s (revisionnages ?) — à vérifier")
    return pubs, erreurs


# ====================================================================== mesures au même âge
def releve_a(p, age):
    """Relevé le plus proche de J+age, si dans la tolérance (± max(1, age/2) jours) ; sinon None."""
    tol = max(1, age / 2)
    cands = [r for r in p["releves"] if abs(r["age"] - age) <= tol]
    return min(cands, key=lambda r: (abs(r["age"] - age), -r["age"])) if cands else None


def _par(n, vues, k=1000):
    return None if n is None or not vues else round(n / vues * k, 2)


def mesures(pubs, age):
    """{pid: {métrique: valeur ou None, 'age': jours}} pour les publications ayant un relevé comparable."""
    out = {}
    for pid, p in pubs.items():
        r = releve_a(p, age)
        if r is None:
            continue
        v = r["vues"]
        out[pid] = {"age": r["age"], "vues": v,
                    "taux_commentaires": _par(r["commentaires"], v), "taux_likes": _par(r["likes"], v),
                    "taux_partages": _par(r["partages"], v), "taux_favoris": _par(r["favoris"], v),
                    "abonnes_1000": _par(r["nouveaux_abonnes"], v), "completion_pct": r["completion_pct"],
                    "part_regardee": None if r["temps_moyen_s"] is None or not p["duree_s"] else round(100 * r["temps_moyen_s"] / p["duree_s"], 1),
                    "revenus_1000": _par(r["revenus_eur"], v), "commentaires": r["commentaires"],
                    "temps_moyen_s": r["temps_moyen_s"]}
    for pid, m in out.items():  # vues relatives à la médiane des AUTRES publications du même compte au même âge
        p = pubs[pid]
        autres = [out[q]["vues"] for q in out if q != pid and out[q]["vues"] and
                  (pubs[q]["compte"], pubs[q]["plateforme"]) == (p["compte"], p["plateforme"])]
        m["indice_vues"] = round(m["vues"] / st.median(autres), 2) if m["vues"] is not None and autres and st.median(autres) else None
    return out


def valeur_dim(p, dim):
    return p.get("tranche") if dim == "duree" else p.get(dim)


# ====================================================================== comparaisons prudentes
def confusions(pubs, avec, sans, exclure=()):
    """Caractéristiques que partagent (≥ 75 %) les publications « avec », et pas les « sans » (≤ 50 %)."""
    out = []
    for dim in DIMENSIONS:
        if dim in exclure:
            continue
        va = [valeur_dim(pubs[q], dim) for q in avec]
        vs = [valeur_dim(pubs[q], dim) for q in sans]
        val, n = Counter(va).most_common(1)[0] if va else (None, 0)
        if val is None or n / len(va) < 0.75:
            continue
        part_sans = vs.count(val) / len(vs) if vs else 0
        if part_sans <= 0.5:
            out.append(f"{DIMENSIONS[dim]} = {val}")
    return out


def comparer_groupe(pubs, M, pred, metrique="indice_vues", exclure=()):
    """Publications où pred est vrai / faux / inconnu (pred → None) : médianes, rapport, confiance, confusions."""
    avec, sans = [], []
    for pid in M:
        x = pred(pubs[pid])
        if x is None or M[pid].get(metrique) is None:
            continue
        (avec if x else sans).append(pid)
    res = {"metrique": metrique, "n_avec": len(avec), "n_sans": len(sans), "avec": avec,
           "projets_avec": len({pubs[q]["projet"] for q in avec}), "ratio": None, "sens": "non mesurable",
           "confiance": "aucune donnée", "confusions": [], "intra_projet": None}
    if not avec:
        return res
    ma = st.median(M[q][metrique] for q in avec)
    res["mediane_avec"] = ma
    if not sans:
        res["confiance"] = "non mesurable (présente dans toutes les vidéos où la mesure existe)"
        return res
    ms = st.median(M[q][metrique] for q in sans)
    res["mediane_sans"] = ms
    if ms:
        res["ratio"] = round(ma / ms, 2)
        res["sens"] = "mieux" if res["ratio"] >= MIEUX else ("moins bien" if res["ratio"] <= MOINS else "pas d'écart net")
    res["confusions"] = confusions(pubs, avec, sans, exclure)
    # Même projet, avec et sans : la comparaison la moins biaisée dont on dispose sans test A/B.
    intra = []
    for proj in {pubs[q]["projet"] for q in avec} & {pubs[q]["projet"] for q in sans}:
        a = [M[q][metrique] for q in avec if pubs[q]["projet"] == proj]
        s = [M[q][metrique] for q in sans if pubs[q]["projet"] == proj]
        if st.median(s):
            intra.append(round(st.median(a) / st.median(s), 2))
    res["intra_projet"] = intra or None
    cote = sum(1 for q in avec if (M[q][metrique] > ms) == (ma > ms)) / len(avec)
    # Comme pour le corpus : une série = une histoire. Il faut 3 projets différents, et 80 % des vidéos du même côté.
    if len(avec) < 3 or res["projets_avec"] < 3:
        res["confiance"] = "hypothèse" + (" (1 seule vidéo)" if len(avec) == 1 else f" ({len(avec)} vidéos, {res['projets_avec']} projet(s))")
    elif res["sens"] in ("mieux", "moins bien") and cote >= 0.8 and not res["confusions"]:
        res["confiance"] = "signal répété"
    else:
        res["confiance"] = "hypothèse (signal mixte ou confondu)"
    return res


def comparaisons(pubs, M, metrique="indice_vues"):
    """{dimension: {valeur: résultat}} + {'mecanique': {id: résultat}}."""
    out = {}
    for dim in DIMENSIONS:
        if dim == "projet":
            continue
        vals = sorted({valeur_dim(pubs[q], dim) for q in M} - {None}, key=str)
        if len(vals) < 2:
            continue
        out[dim] = {v: comparer_groupe(pubs, M, lambda p, d=dim, v=v: None if valeur_dim(p, d) is None else valeur_dim(p, d) == v,
                                       metrique, exclure=(dim,)) for v in vals}
    mecas = sorted({m for q in M for m in (pubs[q]["mecaniques"] or [])})
    out["mecanique"] = {m: comparer_groupe(pubs, M, lambda p, m=m: None if p["mecaniques"] is None else m in p["mecaniques"], metrique)
                        for m in mecas}
    return out


def tendance_compte(pubs, M):
    """Vues de la 2e moitié des publications ÷ 1re moitié (chronologique) : un compte qui grandit biaise les comparaisons."""
    vs = [M[q]["vues"] for q in sorted(M, key=lambda q: pubs[q]["date_publication"]) if M[q]["vues"]]
    if len(vs) < 4:
        return None
    h = len(vs) // 2
    a, b = st.median(vs[:h]), st.median(vs[h:])
    return round(b / a, 2) if a else None


# ====================================================================== apprentissage (bloc calculé seulement)
def apprendre(pubs, M, age, aujourd_hui=None, registre_chemin=None):
    """Écrit resultats_propres dans chaque mécanique. Ne touche à aucun autre champ. Renvoie les ids inconnus."""
    f = Path(registre_chemin or REGISTRE)
    reg = lire_json(f)
    connus = {}
    for m in reg["mecaniques"]:
        connus[m["id"]] = m
        for a in m.get("alias", []):
            connus.setdefault(a, m)
    cites = {x for q in M for x in (pubs[q]["mecaniques"] or [])}
    inconnus = sorted(cites - set(connus))
    if not cites:  # rien à apprendre : on ne touche pas au fichier
        return inconnus
    date = str(aujourd_hui or dt.date.today())
    for m in reg["mecaniques"]:
        ids = {m["id"], *m.get("alias", [])}
        utilise = [q for q in M if pubs[q]["mecaniques"] and ids & set(pubs[q]["mecaniques"])]
        if not utilise:
            m.pop("resultats_propres", None)
            continue
        r = {}
        for met in ("indice_vues", "taux_commentaires", "completion_pct", "part_regardee"):
            g = comparer_groupe(pubs, M, lambda p, ids=ids: None if p["mecaniques"] is None else bool(ids & set(p["mecaniques"])), met)
            if g["n_avec"]:
                r[met] = {"ratio": g["ratio"], "sens": g["sens"], "confiance": g["confiance"],
                          "intra_projet": g["intra_projet"], "confusions": g["confusions"]}
        base = r.get("indice_vues", {})
        m["resultats_propres"] = {
            "maj": date, "age_jours": age, "publications": len(utilise),
            "projets": len({pubs[q]["projet"] for q in utilise}),
            "confiance": base.get("confiance", "aucune donnée"),
            "sens_vues": base.get("sens"), "par_metrique": r, "videos": sorted(utilise),
            "_note": "Calculé par outils/suivi.py sur nos publications (corrélation, jamais une cause). N'affecte ni « preuves » ni les règles.",
        }
    lis = reg.get("_lisez_moi", "")
    if "resultats_propres" not in lis:
        reg["_lisez_moi"] = lis + (" Bloc CALCULÉ par `python3 outils/suivi.py rapport` (ne pas éditer) : « resultats_propres » "
                                   "= résultats de NOS publications (suivi/stats.csv), séparés des preuves du corpus.")
    ecrire_json(f, reg)
    return inconnus


# ====================================================================== rapport
def _f(v, fmt):
    if v is None:
        return "—"
    if fmt == "x":
        return f"×{v:.2f}".replace(".", ",")
    if fmt == "n":
        return f"{v:,}".replace(",", " ")
    return f"{v:g}".replace(".", ",")


def _groupe_txt(nom, g):
    r = f"×{g['ratio']:.2f}".replace(".", ",") if g.get("ratio") is not None else "—"
    x = f"{nom} : {g['n_avec']} vidéo(s) / {g['projets_avec']} projet(s), médiane {r} par rapport aux autres → {g['sens']} · {g['confiance']}"
    if g["confusions"]:
        x += f" · confondu avec : {', '.join(g['confusions'][:2])}" + (f" (+{len(g['confusions']) - 2})" if len(g["confusions"]) > 2 else "")
    if g["intra_projet"]:
        x += f" · dans un même projet : {', '.join('×' + str(v).replace('.', ',') for v in g['intra_projet'])}"
    return x


def rapport(pubs, M, age, inconnus=(), erreurs=(), aujourd_hui=None):
    date = aujourd_hui or dt.date.today()
    L = [f"# Rapport de performances · {date}", ""]
    exclues = [p for p in pubs.values() if p["id"] not in M]
    L += ["## Données", f"- {len(pubs)} publication(s), {sum(len(p['releves']) for p in pubs.values())} relevé(s). "
          f"Comparaison à **J+{age}** (± {max(1, age / 2):g} j) : {len(M)} publication(s) comparable(s)."]
    if exclues:
        L.append("- Exclues (pas de relevé proche de J+%d) : %s." % (age, ", ".join(
            f"{p['id']} (relevés à J+{', J+'.join(str(r['age']) for r in p['releves'])})" for p in exclues)))
    trous = []
    for met, lib in (("commentaires", "commentaires"), ("completion_pct", "complétion"), ("temps_moyen_s", "temps moyen"),
                     ("favoris", "favoris"), ("nouveaux_abonnes", "abonnés"), ("revenus_eur", "revenus")):
        n = sum(1 for q in M if releve_a(pubs[q], age)[met] is not None)
        if M and n < len(M):
            trous.append(f"{lib} {n}/{len(M)}")
    if trous:
        L.append(f"- Données partielles (non estimées, comparaisons limitées aux vidéos renseignées) : {', '.join(trous)}.")
    sans_meca = [q for q in M if pubs[q]["mecaniques"] is None]
    if sans_meca:
        L.append(f"- Mécaniques non renseignées (episode.json sans `mecaniques_utilisees`) pour {len(sans_meca)}/{len(M)} : "
                 "ces vidéos sont exclues des comparaisons de mécaniques (ni « avec » ni « sans »).")
    if inconnus:
        L.append(f"- Mécaniques citées inconnues de bible/mecaniques.json : {', '.join(inconnus)}.")
    for e in erreurs:
        L.append(f"- ⚠ {e}")
    t = tendance_compte(pubs, M)
    L += ["", "**Méthode** : observationnel, petit échantillon. « Mieux » = médiane ≥ ×1,25 par rapport aux autres vidéos, "
          "« moins bien » ≤ ×0,8. Moins de 3 projets = hypothèse ; « signal répété » = 3 vidéos dans 3 projets, 80 % du même "
          "côté, sans variable confondue. Une caractéristique vue dans une seule vidéo n'est pas interprétable seule (annexe B). "
          "Aucune mécanique n'est déclarée responsable d'un résultat."]
    if t and (t >= 2 or t <= 0.5):
        L.append(f"**Attention** : les vidéos récentes font ×{str(t).replace('.', ',')} les anciennes (tendance du compte). "
                 "Tout ce qui a été utilisé surtout récemment (ou surtout au début) paraît meilleur (ou pire) pour cette seule raison.")

    if len(M) < 2:
        L += ["", "Trop peu de publications comparables pour comparer quoi que ce soit. Prochaine étape : saisir les "
              f"relevés à J+{age} de chaque vidéo publiée (`python3 outils/suivi.py ajouter …`)."]
        return "\n".join(L) + "\n"

    ordre = sorted(M, key=lambda q: (M[q]["indice_vues"] is None, -(M[q]["indice_vues"] or M[q]["vues"] or 0)))
    C = comparaisons(pubs, M)
    Ccom = comparaisons(pubs, M, "taux_commentaires")
    Cvis = comparaisons(pubs, M, "completion_pct") if any(M[q]["completion_pct"] is not None for q in M) else \
        comparaisons(pubs, M, "part_regardee")
    groupes = [(dim, v, g) for dim, d in C.items() for v, g in d.items() if g["n_avec"] >= 2]
    uniques = sum(1 for d in C.values() for g in d.values() if g["n_avec"] == 1)

    def nom(dim, v):
        return f"{'mécanique' if dim == 'mecanique' else DIMENSIONS[dim]} « {v} »"

    def classement(met, titre, n=3):
        vals = [(M[q][met], q) for q in M if M[q].get(met) is not None]
        if len(vals) < 2:
            return [f"- {titre} : pas assez de données ({len(vals)} vidéo(s) renseignée(s))."]
        vals.sort(reverse=True)
        return [f"- {titre} : " + " · ".join(f"{pubs[q]['titre']} ({q}) {_f(v, METRIQUES[met][1])}" for v, q in vals[:n])]

    L += ["", "## 1. Ce qui fonctionne le mieux"]
    L += classement("indice_vues", "Vues relatives au compte")
    L += classement("taux_commentaires", "Commentaires pour 1 000 vues")
    L += classement("completion_pct", "Taux de complétion") + classement("part_regardee", "Temps moyen / durée")
    L += classement("taux_partages", "Partages pour 1 000 vues")
    mieux = [(dim, v, g) for dim, v, g in groupes if g["sens"] == "mieux"]
    L += [f"- {_groupe_txt(nom(dim, v), g)}" for dim, v, g in sorted(mieux, key=lambda x: -(x[2]["ratio"] or 0))[:5]] or \
        ["- Aucune caractéristique partagée par 2 vidéos ou plus (hook, fin, moteur, mécanique, format, durée) ne se détache en vues."]

    L += ["", "## 2. Ce qui fonctionne moins bien"]
    bas = [q for q in reversed(ordre) if M[q]["indice_vues"] is not None and M[q]["indice_vues"] <= MOINS][:3]
    L += [f"- {pubs[q]['titre']} ({q}) : {_f(M[q]['indice_vues'], 'x')} la médiane du compte · concept : {pubs[q]['concept'] or '—'}"
          f" · moteur : {pubs[q]['moteur'] or '—'} · hook : {pubs[q]['accroche'] or '—'}" for q in bas] or \
        ["- Aucune vidéo nettement sous la médiane du compte."]
    moins = [(dim, v, g) for dim, v, g in groupes if g["sens"] == "moins bien"]
    L += [f"- {_groupe_txt(nom(dim, v), g)}" for dim, v, g in sorted(moins, key=lambda x: x[2]["ratio"] or 9)[:5]]

    L += ["", "## 3. Hypothèses à tester"]
    hyp = [(dim, v, g) for dim, v, g in groupes if g["sens"] in ("mieux", "moins bien") and g["confiance"].startswith("hypothèse")]
    for met, CC, lib in (("taux_commentaires", Ccom, "commentaires"), ("visionnage", Cvis, "visionnage")):
        hyp += [(dim, v, dict(g, _lib=lib)) for dim, d in CC.items() for v, g in d.items()
                if g["n_avec"] >= 2 and g["sens"] in ("mieux", "moins bien") and g["confiance"].startswith("hypothèse")]
    hyp.sort(key=lambda x: (-x[2]["projets_avec"], -abs((x[2]["ratio"] or 1) - 1)))
    L += [f"- ({g.get('_lib', 'vues')}) {_groupe_txt(nom(dim, v), g)}" for dim, v, g in hyp[:8]] or \
        ["- Aucune piste partagée par 2 vidéos ou plus : continuer à varier hooks, fins et mécaniques."]
    if len(hyp) > 8:
        L.append(f"- … et {len(hyp) - 8} autre(s) en annexe B.")
    if uniques:
        L.append(f"- {uniques} caractéristique(s) n'apparaissent que dans une seule vidéo : pistes brutes, détail en annexe B.")

    def meca_ligne(m, g):
        r = f"×{g['ratio']:.2f}".replace(".", ",") if g.get("ratio") is not None else "—"
        x = f"- `{m}` : {g['n_avec']} vidéo(s) / {g['projets_avec']} projet(s), {r} · {g['confiance']}"
        if g["confusions"]:
            x += f" · confondu avec {len(g['confusions'])} autre(s) caractéristique(s) ({g['confusions'][0]}…)"
        if g["intra_projet"]:
            x += f" · dans un même projet : {', '.join('×' + str(v).replace('.', ',') for v in g['intra_projet'])}"
        return x

    L += ["", "## 4. Mécaniques à réutiliser"]
    reuse = [(m, g) for m, g in C.get("mecanique", {}).items() if g["sens"] == "mieux"]
    reuse += [(m, dict(g, sens="mieux (commentaires)")) for m, g in Ccom.get("mecanique", {}).items()
              if g["sens"] == "mieux" and m not in dict(reuse)]
    L += [meca_ligne(m, g) + ("" if g["confiance"] == "signal répété" else " → réutiliser dans un AUTRE projet pour confirmer")
          for m, g in reuse] or ["- Aucune pour l'instant (pas assez de vidéos où les mécaniques sont renseignées)."]

    L += ["", "## 5. Mécaniques à éviter ou à retravailler"]
    eviter = [(m, g) for m, g in C.get("mecanique", {}).items() if g["sens"] == "moins bien"]
    L += [meca_ligne(m, g) + (" → à retravailler (signal répété)" if g["confiance"] == "signal répété"
                              else " → à surveiller, pas à éviter : une hypothèse ne suffit pas") for m, g in eviter] or \
        ["- Aucune. Rien ne permet d'écarter une mécanique sur nos seuls résultats."]

    L += ["", "## 6. Prochaines expériences recommandées"]
    exp = []
    for m, g in sorted(reuse, key=lambda x: -x[1]["n_avec"])[:2]:
        if g["n_avec"] == 1:
            exp.append(f"Réutiliser `{m}` dans un autre projet (1 seule vidéo : tout le reste est confondu avec elle).")
        elif g["confusions"]:
            exp.append(f"Séparer `{m}` de {g['confusions'][0]} : l'utiliser dans une vidéo qui n'a pas cette caractéristique.")
        elif g["confiance"] != "signal répété":
            exp.append(f"Réutiliser `{m}` dans un projet au moteur narratif différent pour voir si l'écart tient.")
    faibles = [q for q in bas if pubs[q]["hooks_alternatifs"]]
    if any(dim == "accroche" for dim, _, _ in hyp) and not faibles:
        exp.append("Test A/B de hook : republier la même vidéo avec un hook de rechange (colonnes test + variante), relevé à J+2.")
    if faibles:
        q = faibles[0]
        exp.append(f"{pubs[q]['titre']} : refaire seulement le plan 1 avec « {pubs[q]['hooks_alternatifs'][0]} » et reposter "
                   f"(test = {pubs[q]['projet']}-hook, variante = B).")
    if sans_meca:
        exp.append("Renseigner `mecaniques_utilisees` dans les episode.json publiés (liste validée par l'utilisateur) pour pouvoir comparer les mécaniques.")
    if any(M[q]["completion_pct"] is None for q in M):
        exp.append("Relever le taux de complétion et le temps moyen (TikTok Studio → Analyse de la vidéo) : c'est la mesure de rétention la plus directe.")
    deja = {x for q in M for x in (pubs[q]["mecaniques"] or [])}
    try:
        reg = lire_json(REGISTRE)
        jamais = [m["id"] for m in reg["mecaniques"] if (m.get("preuves") or {}).get("niveau") == "recurrente" and m["id"] not in deja]
        if jamais:
            exp.append(f"Mécaniques récurrentes dans le corpus jamais testées chez nous : {', '.join(jamais[:4])}.")
    except (OSError, ValueError):
        pass
    L += [f"{i}. {x}" for i, x in enumerate(exp or ["Publier et relever de nouvelles vidéos : l'échantillon est trop petit."], 1)]

    tests = defaultdict(list)
    for q in M:
        if pubs[q]["test"]:
            tests[pubs[q]["test"]].append(q)
    if tests:
        L += ["", "## Tests A/B (seule source de causalité)"]
        for t, qs in tests.items():
            L.append(f"- {t} : " + " · ".join(f"{pubs[q]['variante']} {_f(M[q]['vues'], 'n')} vues à J+{M[q]['age']}" for q in qs)
                     + (" — une seule variante saisie" if len(qs) < 2 else " → reporter le résultat dans `tests_ab` de la mécanique concernée (champ manuel)"))

    L += ["", "## Annexe A · toutes les publications comparables", "",
          "| Publication | Titre | Durée | Hook | Fin | Moteur | Vues | Relatif | Com/1k | Partages/1k | Complétion | Visionné |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for q in ordre:
        p, m = pubs[q], M[q]
        L.append(f"| {q} (J+{m['age']}) | {p['titre']} | {_f(p['duree_s'], 'd')} s | {p['accroche'] or '—'} | {p['fin'] or '—'} | "
                 f"{p['moteur'] or '—'} | {_f(m['vues'], 'n')} | {_f(m['indice_vues'], 'x')} | {_f(m['taux_commentaires'], 'd')} | "
                 f"{_f(m['taux_partages'], 'd')} | {_f(m['completion_pct'], 'd')} | {_f(m['part_regardee'], 'd')} |")
    L += ["", "## Annexe B · comparaisons détaillées (vues relatives)"]
    for dim, d in C.items():
        L.append(f"\n**{'Mécaniques' if dim == 'mecanique' else DIMENSIONS[dim].capitalize()}**")
        L += [f"- {_groupe_txt(str(v), g)}" for v, g in d.items() if g["n_avec"]]
    return "\n".join(L) + "\n"


def comparer_deux(pubs, a, b, age=None):
    if a not in pubs or b not in pubs:
        raise SystemExit(f"Publications connues : {', '.join(sorted(pubs))}")
    pa, pb = pubs[a], pubs[b]
    ages = sorted({r["age"] for r in pa["releves"]} & {r["age"] for r in pb["releves"]})
    if age is None:
        age = ages[-1] if ages else min(pa["releves"][-1]["age"], pb["releves"][-1]["age"])
    M = mesures({a: pa, b: pb}, age)
    out = [f"Comparaison à J+{age}" + ("" if a in M and b in M else " (au moins une sans relevé proche : comparaison impossible)")]
    for k, lib in (("titre", "titre"), ("concept", "concept"), ("moteur", "moteur"), ("accroche", "hook"), ("fin", "fin"),
                   ("format", "format"), ("rang", "rang"), ("tranche", "durée"), ("mecaniques", "mécaniques"), ("verdict", "Script Doctor")):
        va, vb = pa.get(k), pb.get(k)
        out.append(f"{'≠' if va != vb else ' '} {lib:12} {va} | {vb}")
    for met, (lib, fmt) in METRIQUES.items():
        if met == "indice_vues":
            continue
        out.append(f"  {lib:26} {_f(M.get(a, {}).get(met), fmt)} | {_f(M.get(b, {}).get(met), fmt)}")
    diff = sum(1 for k in ("moteur", "accroche", "fin", "format", "rang", "tranche") if pa.get(k) != pb.get(k))
    out.append(f"\n{diff} caractéristique(s) différente(s) : un écart de résultats ne s'attribue à aucune d'elles en particulier."
               if diff > 1 else "")
    return "\n".join(out)


# ====================================================================== CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ajouter")
    a.add_argument("projet")
    a.add_argument("episode", nargs="?", default="ep001")
    a.add_argument("--publie", required=True)
    a.add_argument("--releve", default=str(dt.date.today()))
    a.add_argument("--plateforme", default="tiktok")
    for c in ("compte", "url", "test", "variante", "notes"):
        a.add_argument(f"--{c}", default="")
    for c, opt in (("vues", "vues"), ("likes", "likes"), ("commentaires", "commentaires"), ("partages", "partages"),
                   ("favoris", "favoris"), ("temps_moyen_s", "temps-moyen"), ("completion_pct", "completion"),
                   ("nouveaux_abonnes", "abonnes"), ("revenus_eur", "revenus"), ("duree_s", "duree")):
        a.add_argument(f"--{opt}", dest=c, default="")
    sub.add_parser("verifier")
    sub.add_parser("liste")
    c = sub.add_parser("comparer")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--age", type=int)
    r = sub.add_parser("rapport")
    r.add_argument("--age", type=int, default=7)
    r.add_argument("--sans-apprentissage", action="store_true")
    o = ap.parse_args(argv)

    if o.cmd == "ajouter":
        ligne = {"projet": o.projet, "episode": o.episode, "plateforme": o.plateforme, "compte": o.compte,
                 "date_publication": o.publie, "date_releve": o.releve, "url": o.url, "test": o.test,
                 "variante": o.variante, "notes": o.notes}
        ligne.update({k: getattr(o, k) for k in ENTIERS + DECIMAUX})
        # Contrôle AVANT d'écrire : on teste le fichier complet avec la nouvelle ligne.
        STATS.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATS.with_suffix(".tmp.csv")
        tmp.write_bytes(STATS.read_bytes() if STATS.exists() else b"")
        try:
            ecrire_ligne(ligne, tmp)
            _, err = charger(tmp)
        finally:
            tmp.unlink(missing_ok=True)
        dures = [e for e in err if "à vérifier" not in e]
        if dures:
            raise SystemExit("Refusé :\n" + "\n".join(dures))
        ecrire_ligne(ligne)
        print(f"Ajouté : {pub_id(o.projet, o.episode, o.plateforme, o.variante)} au {o.releve} → {STATS.as_posix()}")
        for e in err:
            print("attention", e)
        return 0
    pubs, err = charger()
    if o.cmd == "verifier":
        for e in err:
            print("ERREUR", e)
        print(f"{len(pubs)} publication(s), {sum(len(p['releves']) for p in pubs.values())} relevé(s), {len(err)} problème(s)")
        return 1 if err else 0
    if o.cmd == "liste":
        for p in sorted(pubs.values(), key=lambda p: p["date_publication"]):
            r = p["releves"][-1]
            print(f"{p['id']:40} publié {p['date_publication']} · dernier relevé J+{r['age']} : {_f(r['vues'], 'n')} vues, "
                  f"{_f(r['commentaires'], 'n')} com., complétion {_f(r['completion_pct'], 'd')} %")
        return 0
    if o.cmd == "comparer":
        print(comparer_deux(pubs, o.a, o.b, o.age))
        return 0
    M = mesures(pubs, o.age)
    inconnus = [] if o.sans_apprentissage else apprendre(pubs, M, o.age)
    texte = rapport(pubs, M, o.age, inconnus, err)
    RAPPORTS.mkdir(parents=True, exist_ok=True)
    f = RAPPORTS / f"{dt.date.today()}.md"
    f.write_text(texte, encoding="utf-8")
    print(texte)
    print(f"→ {f.as_posix()}" + ("" if o.sans_apprentissage else " · resultats_propres mis à jour dans bible/mecaniques.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
