"""Mécaniques des vidéos analysées : chiffres observables, comparaison au corpus, preuves consolidées.

Python seul (marche sur le cloud, sans les vidéos). Lit :
    analyses/<id>/meta.json, brut.json, transcript.json   (écrits par analyse.py)
    analyses/<id>/mecaniques.json                          (écrit par Claude pendant /analyser)
    analyses/_comptes/<compte>.json                        (vues récentes du compte, écrit par analyse.py)
    bible/mecaniques.json                                  (registre des mécaniques consolidées)

Usage :
    python3 outils/mecaniques.py              # contrôle, puis écrit analyses/MECANIQUES.md et les « preuves » du registre
    python3 outils/mecaniques.py --fiche ID   # bloc A (chiffres) + G (comparaison au corpus) à coller dans la fiche
    python3 outils/mecaniques.py --verifier   # contrôle seulement (code 1 si erreur)

Principes (voir bible/mecaniques.json, « _regles ») :
- une métrique absente reste absente (« non disponible »), jamais estimée ;
- confiance = récurrence sur des COMPTES indépendants, pas un nombre de vidéos ;
- signal de performance = comparaison à l'intérieur d'un même compte, hors suites et compilations : une corrélation,
  déclarée « fragile » si elle change de sens dans un sous-groupe (partie 1, vidéos uniques, hors ton noir).
"""
import argparse
import datetime as dt
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import ANALYSES, BIBLE, ecrire_json, lire_json  # noqa: E402

REGISTRE = BIBLE / "mecaniques.json"
COMPTES = ANALYSES / "_comptes"
RAPPORT = ANALYSES / "MECANIQUES.md"
FORMATS = {"unique", "partie_1", "suite", "compilation", "episode_long"}
HORS_SIGNAL = {"suite", "compilation"}  # vues structurellement différentes : faussent la comparaison


# ---------------------------------------------------------------- chargement
def _lire(p):
    try:
        return lire_json(p) if p.exists() else None
    except ValueError:
        return None


def charger_registre():
    r = lire_json(REGISTRE)
    return r, {m["id"]: m for m in r["mecaniques"]}


def charger_corpus():
    corpus = []
    for d in sorted(p for p in ANALYSES.iterdir() if p.is_dir() and not p.name.startswith("_")):
        brut = _lire(d / "brut.json")
        if not brut:
            continue
        corpus.append({
            "id": d.name,
            "meta": _lire(d / "meta.json") or brut.get("meta") or {},
            "brut": brut,
            "transcript": _lire(d / "transcript.json"),
            "mec": _lire(d / "mecaniques.json"),
        })
    return corpus


def profil_compte(compte):
    p = _lire(COMPTES / f"{compte}.json") if compte else None
    return p if p and p.get("mediane_vues") else None


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


def fmt_de(v):
    return ((v["mec"] or {}).get("contexte") or {}).get("format")


def ctx(v, cle):
    return ((v["mec"] or {}).get("contexte") or {}).get(cle)


# ---------------------------------------------------------------- A. données observables
def metriques(v, corpus):
    m, b, tr = v["meta"], v["brut"], v["transcript"] or {}
    vues = m.get("vues")
    duree = m.get("duree")
    plans = b.get("plans") or []
    durees = [p["duree"] for p in plans]
    phrases = b.get("phrases") or []

    # mots : transcription mot à mot si présente, sinon découpage des phrases ; rien -> non mesuré
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

    # performance relative au compte
    compte = m.get("compte")
    prof = profil_compte(compte)
    ref, src = None, None
    if prof:
        ref, src = prof["mediane_vues"], f"médiane des {prof.get('n', '?')} dernières vidéos du compte ({prof.get('date', '?')})"
    else:
        autres = [w["meta"].get("vues") for w in corpus if w["meta"].get("compte") == compte and w["meta"].get("vues")]
        if len(autres) >= 3:
            ref, src = med(autres), f"médiane des {len(autres)} vidéos analysées du compte (sélection par vues : biaisée vers le haut)"
    abonnes = m.get("abonnes") or (prof or {}).get("abonnes")

    alertes = []
    if len(plans) <= 1 and (duree or 0) > 20:
        alertes.append("1 seul plan détecté sur une vidéo longue : détection probablement ratée (fondus), compter à la main sur la planche")
    if mots is None:
        alertes.append("pas de transcription : mots et débit non mesurés")
    if vues and vues % 100_000 == 0:
        alertes.append("vues arrondies par TikTok (précision ±5 %)")

    return {
        "vues": vues, "likes": m.get("likes"), "commentaires": m.get("commentaires"),
        "partages": m.get("partages"), "favoris": m.get("favoris"), "abonnes": abonnes,
        "taux_likes": taux(m.get("likes"), vues), "taux_commentaires": taux(m.get("commentaires"), vues),
        "taux_partages": taux(m.get("partages"), vues), "taux_favoris": taux(m.get("favoris"), vues),
        "vues_par_abonne": round(vues / abonnes, 2) if vues and abonnes else None,
        "duree": duree, "nombre_plans": len(plans) or None,
        "plan_moyen": round(st.mean(durees), 2) if durees else None,
        "plan_median": round(st.median(durees), 2) if durees else None,
        "plan_max": max(durees) if durees else None,
        "part_plans_courts": round(sum(d < 3 for d in durees) / len(durees) * 100) if durees else None,
        "mots": mots, "mots_par_seconde": round(mots / duree, 2) if mots and duree else None,
        "debit_parle": round(mots / parle, 2) if mots and parle else None,
        "part_parlee": round(parle / duree * 100) if parle and duree else None,
        "plus_long_silence": silence, "premier_mot_a": b.get("premier_mot_a"),
        "indice_compte": round(vues / ref, 2) if vues and ref else None, "reference_compte": src,
        "alertes": alertes,
    }


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
    for a in x["alertes"]:
        L.append(f"> ⚠ {a}")
    return "\n".join(L)


# ---------------------------------------------------------------- preuves
def signal_intra(corpus, pred):
    """Compare, compte par compte, les vidéos où pred est vrai aux autres (hors suites/compilations)."""
    par = defaultdict(lambda: ([], []))
    for v in corpus:
        if not v["mec"] or not v["meta"].get("vues") or fmt_de(v) in HORS_SIGNAL:
            continue
        par[v["meta"].get("compte")][0 if pred(v) else 1].append(v["meta"]["vues"])
    ratios = [med(a) / med(b) for a, b in par.values() if a and b]
    if len(ratios) < 2:
        return {"verdict": "indéterminé", "comptes_contraste": len(ratios), "ratio_median": round(med(ratios), 2) if ratios else None}
    r = med(ratios)
    plus = sum(x > 1 for x in ratios)
    if r >= 1.25 and plus > len(ratios) / 2:
        verdict = "positif"
    elif r <= 0.8 and plus < len(ratios) / 2:
        verdict = "négatif"
    else:
        verdict = "neutre"
    return {"verdict": verdict, "comptes_contraste": len(ratios), "ratio_median": round(r, 2)}


STRATES = {  # sous-groupes où l'on refait la comparaison : un vrai effet ne doit pas changer de sens
    "partie_1": lambda v: fmt_de(v) == "partie_1",
    "unique/long": lambda v: fmt_de(v) in ("unique", "episode_long"),
    "hors ton noir": lambda v: ctx(v, "ton") != "noir",
}


def robustesse(corpus, pred, sig):
    """« robuste » si le signal garde le même sens dans chaque strate mesurable (2+ comptes de contraste)."""
    if sig["verdict"] not in ("positif", "négatif"):
        return "sans objet"
    sens = sig["ratio_median"] > 1
    casses = []
    for nom, f in STRATES.items():
        s = signal_intra([v for v in corpus if f(v)], pred)
        if s["comptes_contraste"] >= 2 and (s["ratio_median"] > 1) != sens:
            casses.append(f"{nom} ×{nb(s['ratio_median'])}")
    return "robuste" if not casses else "fragile : s'inverse en " + ", ".join(casses)


def confiance(comptes, histoires):
    if comptes == 0:
        return "aucune preuve"
    if comptes == 1:
        return "faible"
    if comptes >= 4 and histoires >= 4:
        return "élevé"
    return "moyen"


def resume(occ):
    comptes = {v["meta"].get("compte") for v in occ}
    histoires = {ctx(v, "serie") or v["id"] for v in occ}
    return comptes, histoires


def preuves_de(mid, meca, corpus):
    occ = [v for v in corpus if mid in ids(v)]
    comptes, histoires = resume(occ)
    dom, ton, fmt = (Counter(ctx(v, k) for v in occ if ctx(v, k)) for k in ("domaine", "ton", "format"))
    sig = signal_intra(corpus, lambda v: mid in ids(v))
    sig["robustesse"] = robustesse(corpus, lambda v: mid in ids(v), sig)
    conf = confiance(len(comptes), len(histoires))
    notes = []
    for nom, c in (("domaine", dom), ("ton", ton)):
        if len(occ) >= 3 and c and c.most_common(1)[0][1] / len(occ) >= 0.8:
            notes.append(f"concentrée sur le {nom} « {c.most_common(1)[0][0]} » : effet du contexte possible")
    if len(dom) >= 3:
        notes.append(f"vue dans {len(dom)} domaines")
    if conf == "élevé" and sig["verdict"] == "négatif":
        notes.append("contradiction : fréquente mais sous-performe dans ses propres comptes")
    if meca.get("statut") == "candidate" and len(comptes) >= 2:
        notes.append("candidate vue chez 2 comptes ou plus : à promouvoir « consolidee » après relecture")
    if meca.get("statut") == "consolidee" and len(comptes) <= 1:
        notes.append("consolidée mais 1 seul compte : à repasser « candidate » ou à étayer")
    variantes = {}
    for var in meca.get("variantes", []):
        o = [v for v in occ if any(m["id"] == mid and m.get("variante") == var["id"] for m in v["mec"]["mecaniques"])]
        c, h = resume(o)
        sv = signal_intra(corpus, lambda v, x=var["id"]: any(m["id"] == mid and m.get("variante") == x
                                                           for m in v["mec"]["mecaniques"]))
        variantes[var["id"]] = {"videos": len(o), "comptes": len(c), "confiance": confiance(len(c), len(h)),
                                "signal": sv["verdict"], "ratio": sv["ratio_median"], "comptes_contraste": sv["comptes_contraste"]}
    hors_suite = [v["meta"].get("vues") for v in occ if fmt_de(v) not in HORS_SIGNAL]
    return {
        "maj": dt.date.today().isoformat(),
        "videos": len(occ), "verifiees": sum(bool(v["mec"].get("verifie")) for v in occ),
        "comptes": len(comptes), "histoires": len(histoires),
        "domaines": dict(dom.most_common()), "tons": dict(ton.most_common()), "formats": dict(fmt.most_common()),
        "vues_mediane_hors_suites": med(hors_suite),
        "confiance": conf, "signal_intra_compte": sig,
        "causalite": f"testée ({len(meca['tests_ab'])} test(s) A/B)" if meca.get("tests_ab") else "non établie (observationnel)",
        "variantes": variantes, "notes": notes,
    }


# ---------------------------------------------------------------- contrôle
def verifier(registre, reg, corpus):
    erreurs, avert = [], []
    vus = set()
    for m in registre["mecaniques"]:
        if m["id"] in vus:
            erreurs.append(f"registre : id en double {m['id']}")
        vus.add(m["id"])
        if m.get("type") not in {"narrative", "realisation", "format"}:
            erreurs.append(f"registre : {m['id']} type invalide {m.get('type')}")
        if m.get("statut") not in {"candidate", "consolidee"}:
            erreurs.append(f"registre : {m['id']} statut invalide {m.get('statut')}")
        for champ in ("description", "fonction", "moment", "pourquoi", "transposer", "ne_pas_copier", "limites"):
            if champ not in m:
                erreurs.append(f"registre : {m['id']} sans champ {champ}")
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
        for m in v["mec"].get("mecaniques", []):
            if m["id"] not in reg:
                erreurs.append(f"{v['id']} : mécanique inconnue « {m['id']} » (variante d'une existante ? sinon l'ajouter au registre en candidate)")
            elif m.get("variante") and m["variante"] not in {x["id"] for x in reg[m["id"]].get("variantes", [])}:
                erreurs.append(f"{v['id']} : variante inconnue « {m['id']}/{m['variante']} » (l'ajouter aux variantes du registre)")
    concepts = _lire(BIBLE / "concepts.json") or {}
    for c in concepts.get("concepts", []):
        for mid in c.get("mecaniques", []):
            if mid not in reg:
                erreurs.append(f"concepts.json : {c['id']} cite une mécanique inconnue {mid}")
    return erreurs, avert


# ---------------------------------------------------------------- rapport
def rapport(registre, corpus, P):
    avec = [v for v in corpus if v["mec"]]
    comptes = {v["meta"].get("compte") for v in avec}
    profils = sum(1 for c in comptes if profil_compte(c))
    verif = sum(bool(v["mec"].get("verifie")) for v in avec)
    L = [
        f"# Mécaniques observées — généré le {dt.date.today().strftime('%d/%m/%Y')}",
        "",
        "> Fichier GÉNÉRÉ par `python3 outils/mecaniques.py` : ne pas éditer. Source : `analyses/*/mecaniques.json` + `bible/mecaniques.json`.",
        "",
        f"**Corpus** : {len(avec)} vidéos codées sur {len(corpus)}, {len(comptes)} comptes, {verif} codages vérifiés (fiche v2 ou dissection), "
        f"{len(avec) - verif} rétro-codés depuis les fiches v1. Médiane de compte réelle connue pour {profils} compte(s) sur {len(comptes)}.",
        "",
        "**Biais à garder en tête** : (1) les vidéos ont été choisies parmi les PLUS VUES de chaque compte, donc « présent dans X vidéos à 1 M+ » "
        "décrit les gagnants, pas l'effet de la mécanique ; (2) un seul genre (« fruit drama » FR, 3D, novembre 2026) : un effet "
        "« multi-univers » ne veut dire que plusieurs domaines d'histoire dans ce genre ; (3) les suites perdent des vues par construction : "
        "exclues du signal de performance.",
        "",
        "**Lecture** : *Confiance* = récurrence (faible : 1 compte · moyen : 2-3 comptes · élevé : 4+ comptes et 4+ histoires). "
        "*Signal intra-compte* = vues médianes des vidéos AVEC la mécanique ÷ vidéos SANS, dans le même compte, hors suites ; "
        "« indéterminé » sous 2 comptes de contraste. *Robuste* = le signal garde son sens en partie 1 seule, en vidéos uniques/longues seules "
        "et hors ton noir ; *fragile* = il s'inverse dans un de ces sous-groupes (effet probable du format ou du ton, pas de la mécanique). "
        "Les deux sont des corrélations ; la causalité exige nos propres tests A/B.",
        "",
    ]
    for statut, titre in (("consolidee", "Mécaniques consolidées"), ("candidate", "Candidates (une seule source ou à confirmer)")):
        ms = [m for m in registre["mecaniques"] if m.get("statut") == statut]
        if not ms:
            continue
        L += [f"## {titre}", "",
              "| Mécanique | Type | Vidéos (vérif.) | Comptes | Histoires | Domaines | Vues méd. hors suites | Signal intra-compte | Confiance |",
              "|---|---|---|---|---|---|---|---|---|"]
        for m in sorted(ms, key=lambda m: (-P[m["id"]]["comptes"], -P[m["id"]]["videos"])):
            p = P[m["id"]]
            s = p["signal_intra_compte"]
            sig = f"{s['verdict']}" + (f" ×{nb(s['ratio_median'])} ({s['comptes_contraste']} cpt)" if s["ratio_median"] else "")
            if s.get("robustesse", "sans objet") != "sans objet":
                sig += " · " + ("robuste" if s["robustesse"] == "robuste" else "**fragile**")
            L.append(f"| **{m['nom']}** `{m['id']}` | {m['type']} | {p['videos']} ({p['verifiees']}) | {p['comptes']} | {p['histoires']} | "
                     f"{len(p['domaines'])} | {nb(p['vues_mediane_hors_suites'])} | {sig} | {p['confiance']} |")
        L.append("")
        for m in ms:
            p = P[m["id"]]
            var = " · ".join(f"{k} {x['videos']} vid./{x['comptes']} cpt ({x['confiance']}, signal {x['signal']}"
                             + (f" ×{nb(x['ratio'])}/{x['comptes_contraste']} cpt" if x["ratio"] else "") + ")"
                             for k, x in p["variantes"].items())
            rob = p["signal_intra_compte"].get("robustesse", "")
            lignes = [x for x in (var and f"variantes : {var}", rob.startswith("fragile") and f"signal {rob}", *p["notes"]) if x]
            if lignes:
                L.append(f"- `{m['id']}` : " + " ; ".join(lignes))
        L.append("")

    L += ["## Facteurs de contexte (ton, format, domaine)", "",
          "| Facteur | Vidéos | Comptes | Vues méd. | Signal intra-compte |", "|---|---|---|---|---|"]
    for cle in ("ton", "format", "domaine"):
        for val, n in Counter(ctx(v, cle) for v in avec if ctx(v, cle)).most_common():
            occ = [v for v in avec if ctx(v, cle) == val]
            s = signal_intra(corpus, lambda v, c=cle, x=val: ctx(v, c) == x) if cle != "format" or val not in HORS_SIGNAL \
                else {"verdict": "exclu (suite/compilation)", "ratio_median": None, "comptes_contraste": 0}
            sig = s["verdict"] + (f" ×{nb(s['ratio_median'])} ({s['comptes_contraste']} cpt)" if s["ratio_median"] else "")
            if cle != "format" and s["verdict"] in ("positif", "négatif"):
                r = robustesse(corpus, lambda v, c=cle, x=val: ctx(v, c) == x, s)
                sig += " · " + ("robuste" if r == "robuste" else "fragile (" + r.split(": ", 1)[1] + ")")
            L.append(f"| {cle} : {val} | {n} | {len({v['meta'].get('compte') for v in occ})} | {nb(med(v['meta'].get('vues') for v in occ))} | {sig} |")
    L.append("")
    sans = [v["id"] for v in corpus if not v["mec"]]
    if sans:
        L += ["## Vidéos non codées", "", ", ".join(sans), ""]
    return "\n".join(L)


# ---------------------------------------------------------------- comparaison d'une vidéo au corpus
def bloc_g(v, registre, reg, corpus, P):
    autres = [w for w in corpus if w["id"] != v["id"]]
    L = ["## G. Comparaison au corpus (généré)"]
    if not v["mec"]:
        return "\n".join(L + ["Pas de mecaniques.json pour cette vidéo : l'écrire d'abord."])
    serie = ctx(v, "serie")
    for m in v["mec"]["mecaniques"]:
        if m["id"] not in reg:
            L.append(f"- ❌ `{m['id']}` inconnue du registre")
            continue
        avant = [w for w in autres if m["id"] in ids(w) and not (serie and ctx(w, "serie") == serie)]
        c = {w["meta"].get("compte") for w in avant}
        meme_var = [w for w in avant if any(x["id"] == m["id"] and x.get("variante") == m.get("variante") for x in w["mec"]["mecaniques"])]
        cv = {w["meta"].get("compte") for w in meme_var}
        if not avant:
            etat = "NOUVELLE dans le corpus (hors cette série) : rester « candidate »"
        elif m.get("variante") and not meme_var:
            etat = f"mécanique déjà observée ({len(avant)} vidéos, {len(c)} comptes) ; variante « {m['variante']} » nouvelle"
        elif m.get("variante"):
            etat = (f"mécanique déjà observée ({len(avant)} vidéos, {len(c)} comptes) ; "
                    f"même variante : {len(meme_var)} vidéos, {len(cv)} comptes")
        else:
            etat = f"déjà observée ({len(avant)} vidéos, {len(c)} comptes)"
        autre_compte = bool(c - {v["meta"].get("compte")})
        etat += " ; confirmée par un autre compte" if autre_compte else " ; jamais vue ailleurs que dans ce compte"
        L.append(f"- `{m['id']}{'/' + m['variante'] if m.get('variante') else ''}` : {etat} → confiance globale {P[m['id']]['confiance']}")
    fortes = [m for m in registre["mecaniques"] if P[m["id"]]["confiance"] == "élevé" and m["type"] != "format" and m["id"] not in ids(v)]
    if fortes:
        L.append("- Fréquentes ailleurs, absentes ici : " + ", ".join(f"`{m['id']}`" for m in fortes))
    x = metriques(v, corpus)
    if x["indice_compte"]:
        L.append(f"- Performance dans son compte : ×{nb(x['indice_compte'])} ({x['reference_compte']})")
    return "\n".join(L)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fiche", help="id de vidéo : imprime les blocs A et G")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    registre, reg = charger_registre()
    corpus = charger_corpus()
    erreurs, avert = verifier(registre, reg, corpus)
    for e in erreurs:
        print("ERREUR", e)
    if a.verifier:
        for w in avert:
            print("attention", w)
        print(f"{len(corpus)} vidéos, {len(reg)} mécaniques, {len(erreurs)} erreur(s)")
        raise SystemExit(1 if erreurs else 0)
    P = {mid: preuves_de(mid, m, corpus) for mid, m in reg.items()}
    if a.fiche:
        v = next((w for w in corpus if w["id"] == a.fiche), None)
        if not v:
            raise SystemExit(f"Vidéo inconnue : {a.fiche} (pas de analyses/{a.fiche}/brut.json)")
        print(bloc_a(v, corpus))
        print()
        print(bloc_g(v, registre, reg, corpus, P))
        return
    if erreurs:
        raise SystemExit("Corriger les erreurs avant de régénérer les preuves.")
    for m in registre["mecaniques"]:
        m["preuves"] = P[m["id"]]
    ecrire_json(REGISTRE, registre)
    RAPPORT.write_text(rapport(registre, corpus, P) + "\n", encoding="utf-8")
    print(f"{len(corpus)} vidéos, {len(reg)} mécaniques -> {RAPPORT.relative_to(ANALYSES.parent)} et preuves de {REGISTRE.name}")
    for w in avert:
        print("attention", w)


if __name__ == "__main__":
    main()
