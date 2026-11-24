"""Bibliothèque des mécaniques : chiffres observables, comparaison au corpus, preuves, niveaux, contradictions.

Python seul (marche sur le cloud, sans les vidéos). Lit :
    analyses/<id>/meta.json, brut.json, transcript.json   (écrits par analyse.py)
    analyses/<id>/mecaniques.json                          (écrit par Claude pendant /analyser)
    analyses/_comptes/<compte>.json                        (vues récentes du compte, écrit par analyse.py)
    bible/mecaniques.json                                  (bibliothèque : partie manuelle + preuves calculées)
    bible/concepts.json                                    (contrôle des ids cités)

Usage :
    python3 outils/mecaniques.py              # contrôle, preuves, analyses/MECANIQUES.md, section générée de bible/recettes.md
    python3 outils/mecaniques.py --fiche ID   # blocs A (chiffres) et G (comparaison au corpus) d'une fiche
    python3 outils/mecaniques.py --verifier   # contrôle seulement (code 1 si erreur)
    python3 outils/mecaniques.py --migrer     # réécrit bible/mecaniques.json au format courant (v3)

Principes (bible/mecaniques.json, « _regles ») :
- une métrique absente reste absente (« non disponible »), jamais estimée ;
- niveau = récurrence sur des comptes et des histoires indépendants (a_tester, recurrente, fortement_documentee) ;
- performance = vues avec ÷ sans la mécanique dans un même compte, hors suites : une corrélation, vérifiée dans
  3 sous-groupes (partie 1, vidéos uniques, hors ton noir) ;
- usage = rubrique de lecture : socle, a_tester, contexte, a_eviter (une mécanique est dans UNE rubrique).
"""
import argparse
import datetime as dt
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import ANALYSES, BIBLE, ecrire_json, lire_json  # noqa: E402

REGISTRE = BIBLE / "mecaniques.json"
RECETTES = BIBLE / "recettes.md"
COMPTES = ANALYSES / "_comptes"
RAPPORT = ANALYSES / "MECANIQUES.md"
VERSION = 3
CATEGORIES = ("hook", "narration", "emotion", "retention", "interaction", "realisation", "montage", "format")
FORMATS = {"unique", "partie_1", "suite", "compilation", "episode_long"}
HORS_SIGNAL = {"suite", "compilation"}  # vues structurellement différentes : faussent la comparaison
NIVEAUX = {"a_tester": "à tester (confiance faible)", "recurrente": "récurrente (confiance moyenne)",
           "fortement_documentee": "fortement documentée (confiance élevée)"}
DEBUT = "<!-- BIBLIOTHEQUE:DEBUT -->"
FIN = "<!-- BIBLIOTHEQUE:FIN -->"
ALIAS = {}


# ---------------------------------------------------------------- chargement et migration
def _lire(p):
    try:
        return lire_json(p) if p.exists() else None
    except ValueError:
        return None


def normaliser(m):
    """Mécanique au format v2 (type/statut/fonction/pourquoi…) -> format v3. Sans effet sur une mécanique v3."""
    if "categorie" in m:
        return m

    def joint(*xs):
        return " ".join(x.strip() for x in xs if x and x.strip())
    v3 = {
        "id": m["id"], "nom": m.get("nom", m["id"]),
        "categorie": {"narrative": "narration", "realisation": "realisation", "format": "format"}.get(m.get("type"), "narration"),
        "description": m.get("description", ""),
        "effet": joint(m.get("fonction"), m.get("pourquoi")),
        "fonctionnement": joint(m.get("moment") and f"Moment : {m['moment']}", m.get("transposer") and f"Pour l'appliquer : {m['transposer']}"),
        "conditions": [x for x in (m.get("limites"), m.get("contradictions")) if x],
        "variantes": m.get("variantes", []),
        "erreurs": [m["ne_pas_copier"]] if m.get("ne_pas_copier") else [],
    }
    for k in ("alias", "tests_ab"):
        if m.get(k):
            v3[k] = m[k]
    return v3


def charger_registre():
    r = lire_json(REGISTRE)
    r["mecaniques"] = [normaliser(m) for m in r["mecaniques"]]
    r.setdefault("contradictions", [])
    reg = {m["id"]: m for m in r["mecaniques"]}
    ALIAS.clear()
    ALIAS.update({mid: mid for mid in reg})
    for mid, m in reg.items():
        for a in m.get("alias", []):
            ALIAS.setdefault(a, mid)
    return r, reg


def charger_corpus():
    corpus = []
    for d in sorted(p for p in ANALYSES.iterdir() if p.is_dir() and not p.name.startswith("_")):
        brut = _lire(d / "brut.json")
        if not brut:
            continue
        mec = _lire(d / "mecaniques.json")
        if mec:  # fusions : un ancien id cité par une fiche compte pour la mécanique qui l'a absorbé
            for m in mec.get("mecaniques", []):
                m["id"] = ALIAS.get(m["id"], m["id"])
        corpus.append({"id": d.name, "meta": _lire(d / "meta.json") or brut.get("meta") or {},
                       "brut": brut, "transcript": _lire(d / "transcript.json"), "mec": mec})
    return corpus


def profil_compte(compte):
    p = _lire(COMPTES / f"{compte}.json") if compte else None
    return p if p and p.get("mediane_vues") else None


def ids_concept(c):
    """Ids de mécaniques d'un concept : `mecaniques_ids` (v3) ou `mecaniques` (liste, ancien nom)."""
    x = c.get("mecaniques_ids", c.get("mecaniques"))
    return x if isinstance(x, list) else []


# ---------------------------------------------------------------- utilitaires
def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


def nb(x, dec=2):
    """Nombre à la française ; None -> « non disponible »."""
    if x is None:
        return "non disponible"
    if isinstance(x, (int, float)) and abs(x) >= 1_000_000:
        return f"{x / 1e6:.1f} M".replace(".", ",")
    if isinstance(x, (int, float)) and abs(x) >= 10_000:
        return f"{x / 1e3:.0f} k"
    if isinstance(x, float):
        return f"{x:.{dec}f}".rstrip("0").rstrip(",.").replace(".", ",") or "0"
    return str(x)


def taux(n, vues):
    return round(n / vues * 100, 3) if n is not None and vues else None


def ids(v):
    return {m["id"] for m in (v["mec"] or {}).get("mecaniques", [])}


def ctx(v, cle):
    return ((v["mec"] or {}).get("contexte") or {}).get(cle)


def fmt_de(v):
    return ctx(v, "format")


def compte(v):
    return v["meta"].get("compte")


# ---------------------------------------------------------------- A. données observables
_CACHE = {}


def metriques(v, corpus):
    if v["id"] in _CACHE:
        return _CACHE[v["id"]]
    m, b, tr = v["meta"], v["brut"], v["transcript"] or {}
    vues, duree = m.get("vues"), m.get("duree")
    durees = [p["duree"] for p in b.get("plans") or []]
    phrases = b.get("phrases") or []
    if tr.get("mots"):
        mots = len(tr["mots"])
    elif phrases:
        mots = sum(len(p["texte"].split()) for p in phrases)
    else:
        mots = None
    parle = round(sum(p["fin"] - p["debut"] for p in phrases), 1) if phrases else None
    silence = None
    if phrases and duree:
        bornes = [0.0] + [x for p in phrases for x in (p["debut"], p["fin"])] + [duree]
        silence = round(max(bornes[i + 1] - bornes[i] for i in range(0, len(bornes) - 1, 2)), 1)
    prof = profil_compte(compte(v))
    ref = src = None
    if prof:
        ref, src = prof["mediane_vues"], f"médiane des {prof.get('n', '?')} dernières vidéos du compte ({prof.get('date', '?')})"
    else:
        autres = [w["meta"].get("vues") for w in corpus if compte(w) == compte(v) and w["meta"].get("vues")]
        if len(autres) >= 3:
            ref, src = med(autres), f"médiane des {len(autres)} vidéos analysées du compte (sélection par vues : biaisée vers le haut)"
    abonnes = m.get("abonnes") or (prof or {}).get("abonnes")
    alertes = []
    if len(durees) <= 1 and (duree or 0) > 20:
        alertes.append("1 seul plan détecté sur une vidéo longue : détection probablement ratée (fondus), compter à la main sur la planche")
    if mots is None:
        alertes.append("pas de transcription : mots et débit non mesurés")
    if vues and vues % 100_000 == 0:
        alertes.append("vues arrondies par TikTok (précision ±5 %)")
    x = {
        "vues": vues, "likes": m.get("likes"), "commentaires": m.get("commentaires"),
        "partages": m.get("partages"), "favoris": m.get("favoris"), "abonnes": abonnes,
        "taux_likes": taux(m.get("likes"), vues), "taux_commentaires": taux(m.get("commentaires"), vues),
        "taux_partages": taux(m.get("partages"), vues), "taux_favoris": taux(m.get("favoris"), vues),
        "vues_par_abonne": round(vues / abonnes, 2) if vues and abonnes else None,
        "duree": duree, "nombre_plans": len(durees) or None,
        "plan_moyen": round(st.mean(durees), 2) if durees else None,
        "plan_median": round(st.median(durees), 2) if durees else None,
        "plan_max": max(durees) if durees else None,
        "part_plans_courts": round(sum(d < 3 for d in durees) / len(durees) * 100) if durees else None,
        "mots": mots, "mots_par_seconde": round(mots / duree, 2) if mots and duree else None,
        "debit_parle": round(mots / parle, 2) if mots and parle else None,
        "part_parlee": round(parle / duree * 100) if parle and duree else None,
        "plus_long_silence": silence, "premier_mot_a": b.get("premier_mot_a"),
        "indice_compte": round(vues / ref, 2) if vues and ref else None, "reference_compte": src,
        "intensite": ctx(v, "intensite"), "qualite_visuelle": ctx(v, "qualite_visuelle"),
        "alertes": alertes,
    }
    _CACHE[v["id"]] = x
    return x


def bloc_a(v, corpus):
    x = metriques(v, corpus)
    L = [
        "## A. Données observables",
        "| Mesure | Valeur |", "|---|---|",
        f"| Vues · likes · commentaires · partages · favoris | {nb(x['vues'])} · {nb(x['likes'])} · {nb(x['commentaires'])} · {nb(x['partages'])} · {nb(x['favoris'])} |",
        f"| Taux likes · commentaires · partages · favoris (% des vues) | {nb(x['taux_likes'])} · {nb(x['taux_commentaires'], 3)} · {nb(x['taux_partages'], 3)} · {nb(x['taux_favoris'], 3)} |",
        f"| Abonnés du compte · vues par abonné | {nb(x['abonnes'])} · {nb(x['vues_par_abonne'])} |",
        f"| Performance dans son compte | {('×' + nb(x['indice_compte'])) if x['indice_compte'] else 'non disponible'}{(' (' + x['reference_compte'] + ')') if x['reference_compte'] else ''} |",
        f"| Durée · plans · plan moyen / médian / max | {nb(x['duree'], 1)} s · {nb(x['nombre_plans'])} · {nb(x['plan_moyen'])} / {nb(x['plan_median'])} / {nb(x['plan_max'])} s |",
        f"| Plans de moins de 3 s | {nb(x['part_plans_courts'])} % |",
        f"| Mots · mots/s (total) · débit quand ça parle | {nb(x['mots'])} · {nb(x['mots_par_seconde'])} · {nb(x['debit_parle'])} mots/s |",
        f"| Temps parlé · plus long silence · 1er mot | {nb(x['part_parlee'])} % · {nb(x['plus_long_silence'], 1)} s · {nb(x['premier_mot_a'])} s |",
    ]
    L += [f"> ⚠ {a}" for a in x["alertes"]]
    return "\n".join(L)


# ---------------------------------------------------------------- performance
def signal_intra(corpus, pred):
    """Compare, compte par compte, les vidéos où pred est vrai aux autres (hors suites/compilations)."""
    par = defaultdict(lambda: ([], []))
    for v in corpus:
        if not v["mec"] or not v["meta"].get("vues") or fmt_de(v) in HORS_SIGNAL:
            continue
        par[compte(v)][0 if pred(v) else 1].append(v["meta"]["vues"])
    ratios = [med(a) / med(b) for a, b in par.values() if a and b]
    if len(ratios) < 2:
        return {"verdict": "indéterminé", "comptes_contraste": len(ratios), "ratio_median": round(med(ratios), 2) if ratios else None}
    r = med(ratios)
    plus = sum(x > 1 for x in ratios)
    verdict = ("positif" if r >= 1.25 and plus > len(ratios) / 2 else
               "négatif" if r <= 0.8 and plus < len(ratios) / 2 else "neutre")
    return {"verdict": verdict, "comptes_contraste": len(ratios), "ratio_median": round(r, 2)}


STRATES = {  # sous-groupes où l'on refait la comparaison : un effet réel ne doit pas s'y inverser
    "partie 1": lambda v: fmt_de(v) == "partie_1",
    "vidéo unique": lambda v: fmt_de(v) in ("unique", "episode_long"),
    "hors ton noir": lambda v: ctx(v, "ton") != "noir",
}


def robustesse(corpus, pred, sig):
    """robuste : même verdict dans chaque sous-groupe mesurable ; partiel : neutre dans un sous-groupe ;
    fragile : sens inverse dans un sous-groupe."""
    if sig["verdict"] not in ("positif", "négatif"):
        return "sans objet", []
    inverse, neutre = [], []
    for nom, f in STRATES.items():
        s = signal_intra([v for v in corpus if f(v)], pred)
        if s["comptes_contraste"] < 2:
            continue
        r, haut = s["ratio_median"], sig["ratio_median"] > 1
        if (haut and r < 0.95) or (not haut and r > 1.05):  # sens inverse, au-delà de ±5 %
            inverse.append(f"{nom} ×{nb(r)}")
        elif s["verdict"] != sig["verdict"]:
            neutre.append(f"{nom} ×{nb(r)}")
    if inverse:
        return "fragile", inverse
    return ("partiel", neutre) if neutre else ("robuste", [])


def performance(corpus, pred, occ):
    sig = signal_intra(corpus, pred)
    rob, ou = robustesse(corpus, pred, sig)
    hors = [v for v in occ if fmt_de(v) not in HORS_SIGNAL]
    return {
        "vues_mediane_hors_suites": med(v["meta"].get("vues") for v in hors),
        "taux_commentaires_median": med(metriques(v, corpus)["taux_commentaires"] for v in hors),
        "signal": sig["verdict"], "ratio": sig["ratio_median"], "comptes_contraste": sig["comptes_contraste"],
        "robustesse": rob, "sous_groupes": ou,
    }


def txt_perf(p):
    if p["signal"] == "indéterminé":
        return "effet sur les vues non mesurable (moins de 2 comptes où comparer)"
    s = {"positif": "plus vue", "négatif": "moins vue", "neutre": "pas d'écart net de vues"}[p["signal"]]
    t = f"{s} dans son compte (×{nb(p['ratio'])}, {p['comptes_contraste']} comptes)"
    if p["robustesse"] == "fragile":
        t += f", mais s'inverse en {', '.join(p['sous_groupes'])}"
    elif p["robustesse"] == "partiel":
        t += f", écart non net en {', '.join(p['sous_groupes'])}"
    elif p["robustesse"] == "robuste":
        t += ", stable dans tous les sous-groupes"
    return t


# ---------------------------------------------------------------- niveaux et rubriques
def niveau(comptes, histoires, verif_videos, verif_comptes, contraste):
    if comptes < 2 or histoires < 3:
        manque = []
        if comptes < 2:
            manque.append(f"{2 - comptes} compte de plus" if comptes == 1 else "2 comptes")
        if histoires < 3:
            manque.append(f"{3 - histoires} histoire{'s' * (3 - histoires > 1)} indépendante{'s' * (3 - histoires > 1)} de plus")
        return "a_tester", manque
    manque = [msg for ok, msg in (
        (comptes >= 4, f"{4 - comptes} compte(s) de plus"),
        (histoires >= 6, f"{6 - histoires} histoire(s) de plus"),
        (verif_videos >= 3 and verif_comptes >= 2, f"fiches v2 vérifiées {verif_videos}/3 dans {verif_comptes}/2 comptes"),
        (contraste >= 4, f"performance mesurée sur {contraste}/4 comptes")) if not ok]
    return ("fortement_documentee" if not manque else "recurrente"), manque


def usage(niv, perf, dans_contradiction):
    if perf["signal"] == "négatif" and perf["robustesse"] == "robuste" and perf["comptes_contraste"] >= 4:
        return "a_eviter"
    if dans_contradiction or perf["signal"] == "négatif":
        return "contexte"
    if niv == "a_tester":
        return "a_tester"
    return "socle"


def preuves_de(mid, meca, corpus, registre):
    occ = [v for v in corpus if mid in ids(v)]
    comptes = {compte(v) for v in occ}
    histoires = {ctx(v, "serie") or v["id"] for v in occ}
    verif = [v for v in occ if v["mec"].get("verifie")]
    base = Counter(ctx(v, "ton") for v in corpus if v["mec"])
    tons = Counter(ctx(v, "ton") for v in occ if ctx(v, "ton"))
    doms = Counter(ctx(v, "domaine") for v in occ if ctx(v, "domaine"))
    perf = performance(corpus, lambda v: mid in ids(v), occ)
    niv, manque = niveau(len(comptes), len(histoires), len(verif), len({compte(v) for v in verif}), perf["comptes_contraste"])
    notes = []
    n_base = sum(base.values()) or 1
    if len(occ) >= 3 and tons:
        t, n = tons.most_common(1)[0]
        if n / len(occ) - base[t] / n_base >= 0.25:  # sur-représentation par rapport au corpus
            notes.append(f"sur-représentée dans le ton « {t} » ({n}/{len(occ)} contre {base[t]}/{n_base} dans le corpus)")
    contra = [c["id"] for c in registre.get("contradictions", []) if mid in c.get("mecaniques", [])]
    variantes = {}
    for var in meca.get("variantes", []):
        o = [v for v in occ if any(m["id"] == mid and m.get("variante") == var["id"] for m in v["mec"]["mecaniques"])]
        sv = signal_intra(corpus, lambda v, x=var["id"]: any(m["id"] == mid and m.get("variante") == x for m in v["mec"]["mecaniques"]))
        variantes[var["id"]] = {"videos": len(o), "comptes": len({compte(v) for v in o}),
                                "signal": sv["verdict"], "ratio": sv["ratio_median"], "comptes_contraste": sv["comptes_contraste"]}
    return {
        "maj": dt.date.today().isoformat(),
        "niveau": niv, "manque": manque, "usage": usage(niv, perf, contra),
        "videos": len(occ), "verifiees": len(verif), "comptes": len(comptes), "histoires": len(histoires),
        "sources": [{"id": v["id"], "compte": compte(v), "vues": v["meta"].get("vues"),
                     "variante": next((m.get("variante") for m in v["mec"]["mecaniques"] if m["id"] == mid), None),
                     "verifie": bool(v["mec"].get("verifie"))}
                    for v in sorted(occ, key=lambda v: -(v["meta"].get("vues") or 0))],
        "performance": perf,
        "contexte": {"domaines": dict(doms.most_common()), "tons": dict(tons.most_common()),
                     "formats": dict(Counter(fmt_de(v) for v in occ if fmt_de(v)).most_common())},
        "contradictions": contra,
        "causalite": f"testée ({len(meca['tests_ab'])} test(s) A/B)" if meca.get("tests_ab") else "non établie (observationnel)",
        "variantes": variantes, "notes": notes,
    }


# ---------------------------------------------------------------- contradictions
def selection(v, filtre, corpus):
    x = metriques(v, corpus)
    for k, val in filtre.items():
        if k == "mecanique":
            if val not in ids(v):
                return False
        elif k == "sans_mecanique":
            if val in ids(v):
                return False
        elif k.startswith("contexte."):
            if ctx(v, k.split(".", 1)[1]) not in val:
                return False
        else:
            mesure, (lo, hi) = x.get(k), val
            if mesure is None or (lo is not None and mesure < lo) or (hi is not None and mesure >= hi):
                return False
    return True


def profil_groupe(g, corpus):
    def mm(k, sous=None):
        return med(metriques(v, corpus)[k] for v in (g if sous is None else sous))

    def top(cle):
        return ", ".join(f"{k} {n}" for k, n in Counter(ctx(v, cle) for v in g if ctx(v, cle)).most_common(3))
    hors = [v for v in g if fmt_de(v) not in HORS_SIGNAL]
    codes = {k: sum(ctx(v, k) is not None for v in g) for k in ("intensite", "qualite_visuelle")}
    pct = lambda n: round(n / len(g) * 100) if g else None  # noqa: E731
    return {
        "videos": len(g), "comptes": len({compte(v) for v in g}),
        "vues": mm("vues"), "vues_hors_suites": mm("vues", hors),
        "taux_likes": mm("taux_likes"), "taux_commentaires": mm("taux_commentaires"),
        "taux_commentaires_hors_suites": mm("taux_commentaires", hors), "taux_partages": mm("taux_partages"),
        "part_suites": pct(sum(fmt_de(v) == "suite" for v in g)),
        "formats": top("format"), "domaines": top("domaine"), "tons": top("ton"),
        "duree": mm("duree"), "plan_moyen": mm("plan_moyen"), "mots_par_seconde": mm("mots_par_seconde"),
        "revelation": pct(sum("renversement_statut" in ids(v) for v in g)),
        "intensite": f"{nb(mm('intensite'))} ({codes['intensite']} codées)",
        "qualite_visuelle": f"{nb(mm('qualite_visuelle'))} ({codes['qualite_visuelle']} codées)",
    }


def mesurer_contradiction(c, corpus):
    (na, fa), (nbr, fb) = list(c["groupes"].items())[:2]
    ga = [v for v in corpus if v["mec"] and selection(v, fa, corpus)]
    gb = [v for v in corpus if v["mec"] and selection(v, fb, corpus)]
    ia = {v["id"] for v in ga}
    par = defaultdict(lambda: ([], []))  # comptes qui ont les deux styles, hors suites
    for v in ga + gb:
        if v["meta"].get("vues") and fmt_de(v) not in HORS_SIGNAL:
            par[compte(v)][0 if v["id"] in ia else 1].append(v)
    rv, rc = [], []
    for a, b in par.values():
        if a and b:
            rv.append(med(w["meta"]["vues"] for w in a) / med(w["meta"]["vues"] for w in b))
            ca = med(metriques(w, corpus)["taux_commentaires"] for w in a)
            cb = med(metriques(w, corpus)["taux_commentaires"] for w in b)
            if ca is not None and cb:
                rc.append(ca / cb)
    return {"maj": dt.date.today().isoformat(), na: profil_groupe(ga, corpus), nbr: profil_groupe(gb, corpus),
            "meme_compte": {"comptes": len(rv), "ratio_vues": round(med(rv), 2) if rv else None,
                            "ratio_commentaires": round(med(rc), 2) if rc else None,
                            "lecture": f"{na} ÷ {nbr}, hors suites, comptes qui ont les deux"}}


# ---------------------------------------------------------------- contrôle
def verifier(registre, reg, corpus):
    erreurs, avert = [], []
    vus = set()
    for m in registre["mecaniques"]:
        if m["id"] in vus:
            erreurs.append(f"bibliothèque : id en double {m['id']}")
        vus.add(m["id"])
        if not re.fullmatch(r"[a-z0-9_]+", m["id"]):
            erreurs.append(f"bibliothèque : id non stable « {m['id']} » (minuscules, chiffres, _)")
        if m.get("categorie") not in CATEGORIES:
            erreurs.append(f"bibliothèque : {m['id']} catégorie invalide {m.get('categorie')} (choix : {', '.join(CATEGORIES)})")
        for champ in ("nom", "description", "effet", "fonctionnement"):
            if not m.get(champ):
                erreurs.append(f"bibliothèque : {m['id']} sans {champ}")
        for champ in ("conditions", "variantes", "erreurs"):
            if not isinstance(m.get(champ, []), list):
                erreurs.append(f"bibliothèque : {m['id']}.{champ} doit être une liste")
        vids = [x["id"] for x in m.get("variantes", [])]
        if len(vids) != len(set(vids)):
            erreurs.append(f"bibliothèque : {m['id']} variante en double")
    alias = Counter(a for m in registre["mecaniques"] for a in m.get("alias", []))
    for a, n in alias.items():
        if a in vus or n > 1:
            erreurs.append(f"bibliothèque : alias « {a} » ambigu (déjà un id ou alias de deux mécaniques)")
    for c in registre.get("contradictions", []):
        if len(c.get("groupes", {})) != 2:
            erreurs.append(f"contradiction {c.get('id')} : il faut exactement 2 groupes")
        for champ in ("question", "conditions", "limites", "decision"):
            if not c.get(champ):
                erreurs.append(f"contradiction {c.get('id')} : champ {champ} manquant")
        for mid in c.get("mecaniques", []):
            if mid not in reg:
                erreurs.append(f"contradiction {c.get('id')} : mécanique inconnue {mid}")
    for v in corpus:
        if not v["mec"]:
            avert.append(f"{v['id']} : pas de mecaniques.json")
            continue
        c = v["mec"].get("contexte") or {}
        for k in ("domaine", "ton", "format"):
            if not c.get(k):
                erreurs.append(f"{v['id']} : contexte.{k} manquant")
        if c.get("format") and c["format"] not in FORMATS:
            erreurs.append(f"{v['id']} : format « {c['format']} » hors liste {sorted(FORMATS)}")
        for k in ("intensite", "qualite_visuelle"):
            if c.get(k) is not None and c[k] not in (1, 2, 3):
                erreurs.append(f"{v['id']} : contexte.{k} doit valoir 1, 2 ou 3")
        for m in v["mec"].get("mecaniques", []):
            if m["id"] not in reg:
                erreurs.append(f"{v['id']} : mécanique inconnue « {m['id']} » (chercher une mécanique de même fonction ; sinon l'ajouter)")
            elif m.get("variante") and m["variante"] not in {x["id"] for x in reg[m["id"]].get("variantes", [])}:
                erreurs.append(f"{v['id']} : variante inconnue « {m['id']}/{m['variante']} » (l'ajouter aux variantes)")
    for c in (_lire(BIBLE / "concepts.json") or {}).get("concepts", []):
        for mid in ids_concept(c):
            if ALIAS.get(mid, mid) not in reg:
                erreurs.append(f"concepts.json : {c['id']} cite une mécanique inconnue {mid}")
    return erreurs, avert


# ---------------------------------------------------------------- sorties
def facteurs(corpus):
    """Ton et domaine : effet sur les vues et robustesse (le format est structurel, hors signal)."""
    avec = [v for v in corpus if v["mec"]]
    out = []
    for cle in ("ton", "domaine"):
        for val, n in Counter(ctx(v, cle) for v in avec if ctx(v, cle)).most_common():
            occ = [v for v in avec if ctx(v, cle) == val]
            perf = performance(corpus, lambda v, c=cle, x=val: ctx(v, c) == x, occ)
            out.append({"cle": cle, "val": val, "videos": n, "comptes": len({compte(v) for v in occ}), "perf": perf,
                        "usage": usage("recurrente", perf, False)})
    return out


def rapport(registre, corpus, P, F, C):
    avec = [v for v in corpus if v["mec"]]
    comptes = {compte(v) for v in avec}
    verif = sum(bool(v["mec"].get("verifie")) for v in avec)
    L = [f"# Bibliothèque des mécaniques : rapport détaillé ({dt.date.today().strftime('%d/%m/%Y')})", "",
         "> GÉNÉRÉ par `python3 outils/mecaniques.py` : ne pas éditer. Résumé lisible : section « Bibliothèque des mécaniques » de `bible/recettes.md`.", "",
         f"**Corpus** : {len(avec)} vidéos codées sur {len(corpus)}, {len(comptes)} comptes, {verif} codages vérifiés (fiche v2 ou dissection). "
         f"Médiane de compte réelle connue pour {sum(1 for c in comptes if profil_compte(c))} compte(s).", "",
         "**Biais** : vidéos choisies parmi les plus vues de chaque compte ; un seul genre (fruit drama FR, 3D, nov. 2026) ; "
         "les suites perdent des vues par construction (exclues des comparaisons). Tout est corrélation.", "",
         "## Mécaniques", "",
         "| Mécanique | Catégorie | Niveau | Rubrique | Vidéos (vérif.) | Comptes | Histoires | Vues méd. hors suites | Com. méd. % | Effet sur les vues |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    ordre = {"fortement_documentee": 0, "recurrente": 1, "a_tester": 2}
    for m in sorted(registre["mecaniques"], key=lambda m: (ordre[P[m["id"]]["niveau"]], -P[m["id"]]["comptes"])):
        p = P[m["id"]]
        L.append(f"| **{m['nom']}** `{m['id']}` | {m['categorie']} | {p['niveau']} | {p['usage']} | {p['videos']} ({p['verifiees']}) | "
                 f"{p['comptes']} | {p['histoires']} | {nb(p['performance']['vues_mediane_hors_suites'])} | "
                 f"{nb(p['performance']['taux_commentaires_median'], 3)} | {txt_perf(p['performance'])} |")
    L.append("")
    for m in registre["mecaniques"]:
        p = P[m["id"]]
        var = " · ".join(f"{k} {x['videos']} vid./{x['comptes']} cpt" + (f" (×{nb(x['ratio'])}/{x['comptes_contraste']} cpt)" if x["ratio"] else "")
                         for k, x in p["variantes"].items())
        bits = [b for b in (var and f"variantes : {var}", p["manque"] and "pour monter : " + ", ".join(p["manque"]), *p["notes"]) if b]
        if bits:
            L.append(f"- `{m['id']}` : " + " ; ".join(bits))
    L += ["", "## Contradictions mesurées", ""]
    lignes = [("vidéos · comptes", lambda x: f"{x['videos']} · {x['comptes']}"),
              ("vues méd. (hors suites)", lambda x: f"{nb(x['vues'])} ({nb(x['vues_hors_suites'])})"),
              ("likes % · com. % (com. hors suites)", lambda x: f"{nb(x['taux_likes'])} · {nb(x['taux_commentaires'], 3)} ({nb(x['taux_commentaires_hors_suites'], 3)})"),
              ("part de suites", lambda x: f"{nb(x['part_suites'])} %"),
              ("formats", lambda x: x["formats"]), ("domaines", lambda x: x["domaines"]), ("tons", lambda x: x["tons"]),
              ("durée · plan moyen · mots/s", lambda x: f"{nb(x['duree'], 0)} s · {nb(x['plan_moyen'])} s · {nb(x['mots_par_seconde'])}"),
              ("avec révélation de statut", lambda x: f"{nb(x['revelation'])} %"),
              ("intensité · qualité visuelle (1-3)", lambda x: f"{x['intensite']} · {x['qualite_visuelle']}")]
    for c in registre.get("contradictions", []):
        mes, g = C[c["id"]], list(c["groupes"])
        L += [f"### {c['question']} (`{c['id']}`)", "", "| Mesure | " + " | ".join(g) + " |", "|---|---|---|"]
        L += [f"| {nom} | " + " | ".join(f(mes[k]) for k in g) + " |" for nom, f in lignes]
        mc = mes["meme_compte"]
        L += ["", f"Même compte ({mc['lecture']}) : {mc['comptes']} comptes, vues ×{nb(mc['ratio_vues'])}, commentaires ×{nb(mc['ratio_commentaires'])}.",
              "", "Conditions retenues : " + " ".join(c["conditions"]), "", f"Limites : {c['limites']}", "", f"Décision : {c['decision']}", ""]
    L += ["## Facteurs de contexte (ton, domaine)", "", "| Facteur | Vidéos | Comptes | Effet sur les vues |", "|---|---|---|---|"]
    L += [f"| {f['cle']} : {f['val']} | {f['videos']} | {f['comptes']} | {txt_perf(f['perf'])} |" for f in F]
    sans = [v["id"] for v in corpus if not v["mec"]]
    if sans:
        L += ["", "## Vidéos non codées", "", ", ".join(sans)]
    return "\n".join(L) + "\n"


def section_recettes(registre, corpus, P, F, C):
    avec = [v for v in corpus if v["mec"]]
    rub = defaultdict(list)
    for m in registre["mecaniques"]:
        rub[P[m["id"]]["usage"]].append(m)
    ordre = {"fortement_documentee": 0, "recurrente": 1, "a_tester": 2}

    def tri(ms):
        return sorted(ms, key=lambda m: (ordre[P[m["id"]]["niveau"]], -P[m["id"]]["comptes"]))

    def court(m):
        return f"**{m['nom']}** (`{m['id']}`, {m['categorie']})"

    def n_cpt(p):
        return f"{p['videos']} vidéo{'s' * (p['videos'] > 1)}, {p['comptes']} compte{'s' * (p['comptes'] > 1)}"
    L = [DEBUT,
         f"## Bibliothèque des mécaniques (générée le {dt.date.today().strftime('%d/%m/%Y')} : {len(avec)} vidéos, {len({compte(v) for v in avec})} comptes)",
         "> Section réécrite par `python3 outils/mecaniques.py` depuis `bible/mecaniques.json` (fiche complète de chaque mécanique : "
         "effet, fonctionnement, conditions, variantes, erreurs, sources). Chiffres détaillés : `analyses/MECANIQUES.md`.",
         "> Niveaux : à tester (1 compte ou moins de 3 histoires) · récurrente (2+ comptes, 3+ histoires) · fortement documentée "
         "(4+ comptes, 6+ histoires, 3 fiches v2 vérifiées, performance mesurée sur 4+ comptes). « Plus/moins vue » = dans son "
         "propre compte, hors suites : une corrélation, jamais une preuve de cause. Rien ici n'est obligatoire.", ""]
    L.append("### Ce qu'on retrouve souvent (socle du genre)")
    for m in tri(rub["socle"]):
        p = P[m["id"]]
        L.append(f"- {court(m)} — {NIVEAUX[p['niveau']]}, {n_cpt(p)} · {txt_perf(p['performance'])}.")
    L += ["", "### Mérite d'être testé"]
    for m in tri(rub["a_tester"]):
        p = P[m["id"]]
        L.append(f"- {court(m)} — {n_cpt(p)} · manque {', '.join(p['manque'])}.")
    L += ["", "### Dépend du contexte"]
    for m in tri(rub["contexte"]):
        p = P[m["id"]]
        cs = [x for x in registre["contradictions"] if x["id"] in p["contradictions"]]
        quand = " ".join(x["decision"] for x in cs) or (m["conditions"][0] if m["conditions"] else "")
        L.append(f"- {court(m)} — {NIVEAUX[p['niveau']]}, {n_cpt(p)} · {txt_perf(p['performance'])}. {quand}")
    for f in F:
        if f["comptes"] >= 2 and f["usage"] != "a_eviter" and (f["perf"]["signal"] == "négatif" or f["perf"]["robustesse"] in ("fragile", "partiel")):
            L.append(f"- {f['cle'].capitalize()} « {f['val']} » — {f['comptes']} comptes · {txt_perf(f['perf'])}.")
    for c in registre["contradictions"]:
        if not c.get("mecaniques"):
            L.append(f"- {c['question']} → {c['decision']}")
    L += ["", "### À éviter"]
    ev = [court(m) + " — " + txt_perf(P[m["id"]]["performance"]) for m in rub["a_eviter"]]
    ev += [f"{f['cle'].capitalize()} « {f['val']} » — {txt_perf(f['perf'])}" for f in F if f["usage"] == "a_eviter"]
    L += [f"- {x}." for x in ev] or ["- Aucun facteur négatif stable mesuré à ce jour."]
    L.append("- Erreurs connues : champ `erreurs` de chaque mécanique (`bible/mecaniques.json`) et section « Conformité » de ce fichier.")
    if not any(P[m["id"]]["niveau"] == "fortement_documentee" for m in registre["mecaniques"]):
        proches = sorted((m for m in registre["mecaniques"] if P[m["id"]]["niveau"] == "recurrente"),
                         key=lambda m: (len(P[m["id"]]["manque"]), -P[m["id"]]["comptes"]))[:3]
        L += ["", "Aucune mécanique fortement documentée : les codages viennent surtout des fiches v1 non vérifiées. Les plus proches : "
              + " ; ".join(f"`{m['id']}` (manque {', '.join(P[m['id']]['manque'])})" for m in proches) + "."]
    L.append(FIN)
    return "\n".join(L)


def ecrire_recettes(section):
    txt = RECETTES.read_text(encoding="utf-8") if RECETTES.exists() else "# Recettes virales\n"
    if DEBUT in txt and FIN in txt:
        a, b = txt.index(DEBUT), txt.index(FIN) + len(FIN)
        txt = txt[:a] + section + txt[b:]
    else:  # première fois, ou recettes.md réécrit sans la section : elle va juste après le titre
        tete, _, reste = txt.partition("\n")
        txt = tete + "\n\n" + section + "\n\n" + reste.lstrip("\n")
    RECETTES.write_text(txt, encoding="utf-8")


def bloc_g(v, registre, reg, corpus, P):
    autres = [w for w in corpus if w["id"] != v["id"]]
    L = ["## G. Comparaison au corpus (généré)"]
    if not v["mec"]:
        return "\n".join(L + ["Pas de mecaniques.json pour cette vidéo : l'écrire d'abord."])
    serie = ctx(v, "serie")
    for m in v["mec"]["mecaniques"]:
        if m["id"] not in reg:
            L.append(f"- ❌ `{m['id']}` inconnue de la bibliothèque")
            continue
        avant = [w for w in autres if m["id"] in ids(w) and not (serie and ctx(w, "serie") == serie)]
        c = {compte(w) for w in avant}
        meme_var = [w for w in avant if any(x["id"] == m["id"] and x.get("variante") == m.get("variante") for x in w["mec"]["mecaniques"])]
        if not avant:
            etat = "NOUVELLE dans le corpus (hors cette série)"
        elif m.get("variante") and not meme_var:
            etat = f"mécanique déjà observée ({len(avant)} vidéos, {len(c)} comptes) ; variante « {m['variante']} » nouvelle"
        elif m.get("variante"):
            etat = (f"mécanique déjà observée ({len(avant)} vidéos, {len(c)} comptes) ; même variante : "
                    f"{len(meme_var)} vidéos, {len({compte(w) for w in meme_var})} comptes")
        else:
            etat = f"déjà observée ({len(avant)} vidéos, {len(c)} comptes)"
        etat += " ; confirmée par un autre compte" if c - {compte(v)} else " ; jamais vue ailleurs que dans ce compte"
        L.append(f"- `{m['id']}{'/' + m['variante'] if m.get('variante') else ''}` : {etat} → {P[m['id']]['niveau']}, rubrique {P[m['id']]['usage']}")
    absentes = [m for m in registre["mecaniques"] if P[m["id"]]["niveau"] != "a_tester" and m["categorie"] != "format" and m["id"] not in ids(v)]
    if absentes:
        L.append("- Récurrentes ailleurs, absentes ici : " + ", ".join(f"`{m['id']}`" for m in absentes))
    x = metriques(v, corpus)
    if x["indice_compte"]:
        L.append(f"- Performance dans son compte : ×{nb(x['indice_compte'])} ({x['reference_compte']})")
    return "\n".join(L)


def calculer(registre, reg, corpus):
    P = {mid: preuves_de(mid, m, corpus, registre) for mid, m in reg.items()}
    F = facteurs(corpus)
    C = {c["id"]: mesurer_contradiction(c, corpus) for c in registre["contradictions"]}
    return P, F, C


_REG = {}


def infos(mid):
    """Pour verifier.py : (id canonique, niveau, usage) ou None si inconnu. Lit les preuves déjà calculées."""
    if not _REG:
        _REG.update(charger_registre()[1])
    reg = _REG
    cid = ALIAS.get(mid)
    if not cid:
        return None
    p = reg[cid].get("preuves") or {}
    return cid, p.get("niveau"), p.get("usage")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fiche", help="id de vidéo : imprime les blocs A et G")
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--migrer", action="store_true", help="réécrit bible/mecaniques.json au format v3")
    a = ap.parse_args()
    registre, reg = charger_registre()
    if a.migrer:
        registre["version"] = VERSION
        for m in registre["mecaniques"]:
            m.pop("preuves", None)
        ecrire_json(REGISTRE, registre)
        print(f"bibliothèque migrée au format v{VERSION} : {len(reg)} mécaniques (lancer ensuite sans option pour les preuves)")
        return
    corpus = charger_corpus()
    erreurs, avert = verifier(registre, reg, corpus)
    for e in erreurs:
        print("ERREUR", e)
    if a.verifier:
        for w in avert:
            print("attention", w)
        print(f"{len(corpus)} vidéos, {len(reg)} mécaniques, {len(registre['contradictions'])} contradictions, {len(erreurs)} erreur(s)")
        raise SystemExit(1 if erreurs else 0)
    if erreurs:
        raise SystemExit("Corriger les erreurs avant de régénérer.")
    P, F, C = calculer(registre, reg, corpus)
    if a.fiche:
        v = next((w for w in corpus if w["id"] == a.fiche), None)
        if not v:
            raise SystemExit(f"Vidéo inconnue : {a.fiche} (pas de analyses/{a.fiche}/brut.json)")
        print(bloc_a(v, corpus))
        print()
        print(bloc_g(v, registre, reg, corpus, P))
        return
    for m in registre["mecaniques"]:
        m["preuves"] = P[m["id"]]
    for c in registre["contradictions"]:
        c["mesures"] = C[c["id"]]
    registre["version"] = VERSION
    ecrire_json(REGISTRE, registre)
    RAPPORT.write_text(rapport(registre, corpus, P, F, C), encoding="utf-8")
    ecrire_recettes(section_recettes(registre, corpus, P, F, C))
    print(f"{len(corpus)} vidéos, {len(reg)} mécaniques -> {REGISTRE.name} (preuves), {RAPPORT.name}, section de {RECETTES.name}")
    for w in avert:
        print("attention", w)


if __name__ == "__main__":
    main()
