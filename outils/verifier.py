"""Contrôle qualité d'un épisode AVANT de produire le pack.

Usage : python outils/verifier.py <projet> [epNNN]   (ep001 par défaut)
Sortie : liste OK / ÉCHEC / À VOIR, code de sortie 1 s'il y a un échec.
Vérifie : structure, accroche, cliffhanger, rythme et variété (cadrages, caméras, angles, lieux,
lumières, parole), cohérence des tenues, et non-répétition par rapport aux épisodes précédents.
"""
import re
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from itertools import groupby
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bible import Bible  # noqa: E402
from commun import ANALYSES, args_projet, compat_plan, dialogues, duree_plan, lire_json  # noqa: E402

PROCHES = {"TGP", "GP", "PR"}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).strip()


def historique(b, numero):
    f = b.episodes / "historique.json"
    if not f.exists():
        return []
    return sorted((e for e in lire_json(f) if e["numero"] < numero), key=lambda e: e["numero"])


def verifier(projet, nom):
    b = Bible(projet)
    ep = lire_json(b.episodes / nom / "episode.json")
    bruts = ep["plans"]
    plans = [compat_plan(p) for p in bruts]
    hist = historique(b, ep["numero"]) if b.serie else []
    res = []  # (niveau, règle, mesure)

    def ok(cond, regle, mesure, niveau="ÉCHEC"):
        res.append(("OK" if cond else niveau, regle, mesure))

    r = b.real
    # Adaptation (/copier) : on suit le rythme et la structure de la vidéo source, donc les règles de
    # format de /creer deviennent des avertissements (À VOIR) ; le contrôle anti-copie s'ajoute à la fin.
    adapt = ep.get("adaptation") or b.projet.get("adaptation")  # série source : une vidéo par épisode
    souple = "À VOIR" if adapt else "ÉCHEC"
    # ---------- structure ----------
    if adapt:
        ok(4 <= len(plans) <= 40, "4 à 40 plans (adaptation : suit la source)", len(plans))
    else:
        ok(12 <= len(plans) <= 16, "12 à 16 plans", len(plans))
    erreurs = []
    for p in plans:
        for champ, table in (("lieu", b.lieux), ("lumiere", r["lumieres"]), ("cadrage", r["cadrages"]),
                             ("angle", r["angles"]), ("camera", r["cameras"])):
            if p.get(champ) not in table:
                erreurs.append(f"plan {p['n']} {champ}={p.get(champ)}")
        for pe in p.get("persos", []):
            if pe["id"] not in b.persos:
                erreurs.append(f"plan {p['n']} perso inconnu {pe['id']}")
            elif pe.get("tenue", "base") not in b.persos[pe["id"]]["tenues"]:
                erreurs.append(f"plan {p['n']} tenue {pe.get('tenue')} de {pe['id']}")
            if not pe.get("jeu"):
                erreurs.append(f"plan {p['n']} jeu vide pour {pe['id']}")
        presents = {x["id"] for x in p.get("persos", [])} | {x["id"] for x in p.get("fin", {}).get("persos", [])}
        for d in dialogues(p):
            if d.get("parle") not in presents and not d.get("hors_champ"):
                erreurs.append(f"plan {p['n']} : {d.get('parle')} parle mais n'est pas dans l'image")
        if not p.get("mouvement") and not p.get("timeline"):
            erreurs.append(f"plan {p['n']} mouvement vide")
    ok(not erreurs, "Codes valides (bible, réalisation)", "; ".join(erreurs) or "oui")

    maxi = 18 if adapt else 12
    longs = [f"{p['n']}:{len(d['texte'].split())}" for p in plans for d in dialogues(p)
             if not 1 <= len(d["texte"].split()) <= maxi]
    ok(not longs, f"Chaque réplique de 1 à {maxi} mots (punchy)", ", ".join(longs) or "oui")

    # ---------- dynamisme TikTok (durées, timecodes, ping-pong) ----------
    durees = [duree_plan(p) for p in plans]
    ok(all(d in (6, 10) for d in durees), "Durées Grok valides (6 ou 10 s)", durees)
    ok(durees.count(10) >= 2 and durees.count(6) >= 4, "Durées variées : 2+ plans de 10 s ET 4+ de 6 s",
       f"{durees.count(6)}×6 s, {durees.count(10)}×10 s", souple)
    tot = sum(durees)
    ok(68 <= tot <= 92, "Rush total 68 à 92 s (≈ 61-75 s après montage)", f"{tot} s", souple)
    sans_fin = [p["n"] for p in plans if duree_plan(p) == 10 and not p.get("fin")]
    ok(not sans_fin, "Chaque plan de 10 s a une image de fin (fin)", sans_fin or "oui")
    hors, debit, lents = [], [], []
    for p in bruts:
        d = duree_plan(p)
        for x in (p.get("timeline") or []) + dialogues(p):
            a, _, z = str(x["t"]).partition("-")
            try:
                a, z = float(a), float(z or a)
            except ValueError:
                hors.append(f"{p['n']}:{x['t']}")
                continue
            if not 0 <= a <= z <= d:
                hors.append(f"{p['n']}:{x['t']}")
            if x.get("texte") and z > a and len(x["texte"].split()) / (z - a) > 4.2 + 1e-9:
                debit.append(f"{p['n']}:« {x['texte'][:25]}… » {len(x['texte'].split()) / (z - a):.1f} mots/s")
        if len(p.get("timeline") or []) < -(-d // 3):
            lents.append(f"{p['n']}:{len(p.get('timeline') or [])}/{-(-d // 3)}")
    ok(not hors, "Timecodes valides et dans la durée du plan", ", ".join(hors) or "oui")
    ok(not debit, "Débit parlé tenable (4,2 mots/s max, rythme des vidéos virales analysées)", "; ".join(debit) or "oui")
    ok(not lents, "Un nouveau temps fort toutes les 3 s max (timeline)", ", ".join(lents) or "oui")
    pingpong = sum(1 for p in plans if len({d["parle"] for d in dialogues(p)}) >= 2)
    ok(pingpong >= 4, "4+ plans en ping-pong (2 personnages se répondent)", pingpong)
    d1 = dialogues(bruts[0])
    ok(bool(d1) and float(str(d1[0]["t"]).split("-")[0]) <= 0.5, "1re réplique dès 0,5 s max",
       d1[0]["t"] if d1 else "—")
    # ---------- moteur d'histoire et dialogues (recettes.md) ----------
    mo = ep.get("moteur") or {}
    manque = [k for k in ("desir", "injustice", "antagoniste", "enjeu_chiffre", "force_cachee", "payoff", "callback", "kicker")
              if not mo.get(k)]
    ok(not manque, "Moteur d'histoire complet (injustice, antagoniste, enjeu, payoff, callback…)", manque or "oui")
    fonctions = Counter(d.get("fonction", "?") for p in bruts for d in dialogues(p))
    sans = fonctions.get("?", 0) + fonctions.get("info", 0)
    ok(sans == 0, "Chaque réplique a une fonction (jamais « info »)", dict(fonctions))
    clash = sum(1 for p in bruts for a_, b_ in zip(dialogues(p), dialogues(p)[1:])
                if a_.get("fonction") in ("attaque", "menace") and b_.get("fonction") == "riposte" and a_["parle"] != b_["parle"])
    ok(clash >= 4, "4+ clashs attaque → riposte", clash, souple)
    if mo.get("callback"):
        cb = norm(mo["callback"])
        n_cb = sum(1 for p in bruts for d in dialogues(p) if cb and cb in norm(d["texte"]))
        ok(n_cb >= 2, "La phrase-signature du méchant revient au payoff (callback 2 fois)", n_cb, souple)
    mous, trous = [], []
    for p in bruts:
        ds = dialogues(p)
        if not ds:
            continue
        iv = sorted((float(str(d["t"]).split("-")[0]), float(str(d["t"]).split("-")[-1])) for d in ds)
        parle = sum(z - a for a, z in iv)
        if parle / duree_plan(p) < 0.55:
            mous.append(f"{p['n']}:{int(100 * parle / duree_plan(p))}%")
        gaps = [iv[0][0]] + [b2[0] - a2[1] for a2, b2 in zip(iv, iv[1:])]
        if max(gaps) > 1.5:
            trous.append(f"{p['n']}:{max(gaps):.1f}s")
    ok(not mous, "Parole sur 55 %+ de chaque plan parlé", ", ".join(mous) or "oui")
    ok(not trous, "Jamais plus de 1,5 s de silence dans un plan parlé", ", ".join(trous) or "oui")
    ok(len(ep.get("hooks_alternatifs", [])) >= 3, "3 hooks de rechange (A/B test)", len(ep.get("hooks_alternatifs", [])))
    ok(any(p.get("texte_decor") for p in plans), "Au moins un gros chiffre/texte lisible dans le décor",
       sum(1 for p in plans if p.get("texte_decor")), "À VOIR")
    muets = sum(1 for p in plans if not p.get("replique"))
    ok(muets <= 1, "Au plus 1 plan muet", muets)

    p1 = plans[0]
    h1 = (dialogues(bruts[0]) or [{"texte": ""}])[0]["texte"]
    ok(bool(h1) and len(h1.split()) <= 12, "1re réplique d'accroche, 12 mots max", h1 or "—")
    ok(p1["cadrage"] in PROCHES | {"ECRAN", "INSERT"}, "Plan 1 serré (visage, écran ou objet)", p1["cadrage"])
    ok(ep.get("accroche_type") in r["accroches"], "Type d'accroche déclaré", ep.get("accroche_type"))
    ok(ep.get("cliff_type") in r["cliffhangers"], "Type de cliffhanger déclaré", ep.get("cliff_type"))
    ok(plans[-1].get("role") == "cliff", "Dernier plan = cliffhanger", plans[-1].get("role"))
    ce = ep.get("commentaire_epingle", "")
    ok("/" in ce or "?" in ce, "Question de vote en commentaire épinglé", ce or "—")

    # ---------- rythme et variété ----------
    cad = [p["cadrage"] for p in plans]
    rep = [f"{i + 1}-{i + 2}" for i in range(len(cad) - 1) if cad[i] == cad[i + 1]]
    ok(not rep, "Jamais 2 cadrages identiques d'affilée", ", ".join(rep) or "oui")
    ok(len(set(cad)) >= 5, "Au moins 5 cadrages différents", len(set(cad)))
    ok(sum(c in PROCHES for c in cad) >= 4, "Au moins 4 plans serrés sur les visages",
       sum(c in PROCHES for c in cad))
    cams = [p["camera"] for p in plans]
    ok(len(set(cams)) >= 4, "Au moins 4 mouvements de caméra différents", len(set(cams)))
    fixes = max((sum(1 for _ in g) for k, g in groupby(cams) if k == "fixe"), default=0)
    ok(fixes < 3, "Jamais 3 caméras fixes d'affilée", fixes)
    ok(cams.count("zoom_dramatique") <= 1, "Zoom dramatique 1 fois max", cams.count("zoom_dramatique"))
    angles = {p.get("angle", "face") for p in plans}
    ok(len(angles) >= 3, "Au moins 3 angles différents", len(angles))
    lieux = [p["lieu"] for p in plans]
    huis_clos = "huis clos" in ep.get("format", "")
    ok(len(set(lieux)) >= (1 if huis_clos else 3), "Au moins 3 lieux (sauf huis clos)", len(set(lieux)), souple)
    ok(len({p["lumiere"] for p in plans}) >= 2, "Au moins 2 lumières", len({p["lumiere"] for p in plans}))
    parleurs = [d["parle"] for p in plans for d in dialogues(p)]
    suite = max((sum(1 for _ in g) for _, g in groupby(parleurs)), default=0)
    ok(suite <= 4, "Même personnage 4 répliques d'affilée max", suite)
    ok(len(set(parleurs)) >= 3, "Au moins 3 personnages parlent", len(set(parleurs)), souple)
    tous = {pe["id"] for p in plans for pe in p["persos"] + p.get("fin", {}).get("persos", [])}
    ok(len(tous) <= 6, "6 personnages max dans l'épisode", len(tous))

    # continuité des tenues : même perso, même lieu, même tenue
    vu, conflits = {}, []
    for p in plans:
        for pe in p["persos"]:
            k = (pe["id"], p["lieu"])
            t = pe.get("tenue", "base")
            if k in vu and vu[k] != t and "flashback" not in ep.get("format", ""):
                conflits.append(f"{pe['id']} plan {p['n']}")
            vu.setdefault(k, t)
    ok(not conflits, "Tenues cohérentes dans un même lieu", ", ".join(conflits) or "oui")

    # ---------- série : pas de répétition ----------
    fils = {f["id"]: f for f in b.saison["fils"]}
    av = ep.get("fils_avances", [])
    if b.serie:
        ok(bool(av) and all(f in fils for f in av), "Fait avancer au moins un fil de la saison", ", ".join(av) or "aucun")
    rev = [f for f in ep.get("revele", []) if fils.get(f, {}).get("statut") == "cache"]
    ok(len(rev) <= 1, "Un seul secret révélé max", ", ".join(rev) or "aucun")
    if hist:
        der = hist[-1]
        ok(ep.get("format") not in [h.get("format") for h in hist[-2:]], "Format différent des 2 derniers épisodes",
           ep.get("format"))
        ok(ep.get("accroche_type") not in [h.get("accroche_type") for h in hist[-3:]],
           "Accroche différente des 3 derniers", ep.get("accroche_type"))
        ok(ep.get("cliff_type") not in [h.get("cliff_type") for h in hist[-3:]],
           "Cliffhanger différent des 3 derniers", ep.get("cliff_type"))
        principal = Counter(lieux).most_common(1)[0][0]
        ok(principal != der.get("lieu_principal"), "Décor principal différent de l'épisode précédent", principal)
        ok(ep.get("centre") != der.get("centre"), "Personnage au centre différent de l'épisode précédent",
           ep.get("centre"))
        anciennes = {norm(x) for h in hist for x in h.get("repliques", [])}
        doublons = [p["n"] for p in plans if p.get("replique") and norm(p["replique"]) in anciennes]
        ok(not doublons, "Aucune réplique déjà utilisée", doublons or "oui")
        ok(bool(ep.get("reprend")), "Reprend la fin de l'épisode précédent", ep.get("reprend", "—"), "À VOIR")
    # ---------- rétention ----------
    ta = ep.get("texte_accroche", "")
    ok(bool(ta) and len(ta.split()) <= 7, "Texte d'accroche à l'écran (7 mots max)", ta or "—")
    qm = ep.get("question_milieu") or {}
    ok(bool(qm.get("texte")) and 5 <= int(qm.get("plan", 0)) <= 8, "Question au milieu de la vidéo (plans 5 à 8)",
       f"plan {qm.get('plan')} : {qm.get('texte', '—')}", souple)
    ret = [p["n"] for p in plans if p.get("role") == "retournement"]
    ok(any(3 <= n <= 6 for n in ret) and any(7 <= n <= 11 for n in ret),
       "Retournement avant 35 s ET avant 65 s", ret or "aucun", souple)
    if b.serie:
        ok(f"#partie{ep['numero']}" in [h.lower() for h in ep.get("hashtags", [])], "Hashtag #partieN", ep.get("hashtags"))

    # ---------- conformité TikTok (bible/conformite.json) ----------
    c = b.conf

    def mots(x):
        x = unicodedata.normalize("NFD", str(x).lower())
        x = "".join(ch for ch in x if unicodedata.category(ch) != "Mn")
        return " " + re.sub(r"[^a-z0-9]+", " ", x).strip() + " "

    def trouve(texte, liste):
        t = mots(texte)
        return [m for m in liste if mots(m) in t]

    textes = [(f"plan {p['n']}", " ".join(str(p.get(k, "")) for k in ("replique", "jeu_txt", "mouvement", "detail_image", "texte_decor", "texte_ecran"))
               + " " + " ".join(e.get("action", "") for e in p.get("timeline") or [])
               + " " + " ".join(x.get("jeu", "") for x in p.get("persos", []))) for p in plans]
    textes += [(k, str(ep.get(k, ""))) for k in ("titre", "titre_couverture", "legende", "commentaire_epingle", "texte_accroche")]
    textes.append(("question_milieu", qm.get("texte", "")))
    rouges = []
    for ou, t in textes:
        for cat, liste in c.get("rouge", {}).items():
            for m in trouve(t, liste):
                rouges.append(f"{ou} « {m} » ({cat}) → {c.get('remplacements', {}).get(mots(m).strip(), 'reformuler')}")
    ok(not rouges, "Aucun mot rouge TikTok (insulte dégradante, haine, menace, sexe, drogue)", "; ".join(rouges) or "oui")
    oranges = [(f"plan {p['n']}", m) for p in plans for m in trouve(p.get("replique", ""), c.get("orange", []))]
    ok(len(oranges) <= c.get("max_orange", 2), f"Mots orange {c.get('max_orange', 2)} max par épisode",
       ", ".join(f"{o} « {m} »" for o, m in oranges) or 0)
    ok(not trouve(plans[0].get("replique", ""), c.get("orange", [])), "Plan 1 sans gros mot", plans[0].get("replique", ""))
    bait = [m for k in ("legende", "commentaire_epingle") for m in trouve(ep.get(k, ""), c.get("appats_interdits", []))]
    bait += trouve(qm.get("texte", ""), c.get("appats_interdits", []))
    ok(not bait, "Pas d'appât à likes/abonnements (inéligible Pour Toi)", ", ".join(bait) or "oui")
    ok(4 <= len(ep.get("hashtags", [])) <= 7, "4 à 7 hashtags", len(ep.get("hashtags", [])), "À VOIR")

    fet = Counter()
    for p in plans:
        for pid, x in b.persos.items():
            if (p.get("replique") and x.get("replique_fetiche") and norm(x["replique_fetiche"]) in norm(p["replique"])
                    and norm(x["replique_fetiche"]) != norm((ep.get("moteur") or {}).get("callback", ""))):
                fet[pid] += 1
    ok(max(fet.values(), default=0) <= 2, "Réplique fétiche 2 fois max par personnage", dict(fet) or 0, "À VOIR")
    if adapt:
        res += verifier_adaptation(b, ep, adapt)
    return res


def plage(txt):
    """"r1-r32" -> [1..32]."""
    a, _, z = str(txt).replace("r", "").partition("-")
    return list(range(int(a), int(z or a) + 1))


def verifier_adaptation(b, ep, adapt):
    """Fidélité à la source (chaque réplique source est reprise) ET distance (aucune réplique recopiée)."""
    res = []

    def ok(cond, regle, mesure, niveau="ÉCHEC"):
        res.append(("OK" if cond else niveau, regle, mesure))

    f = ANALYSES / str(adapt.get("source")) / "dissection.json"
    if not f.exists():
        ok(False, "Dissection de la source présente", f"{f} introuvable (lancer /copier)")
        return res
    dis = lire_json(f)
    src = {x["r"]: x["texte"] for x in dis.get("repliques", [])}
    lignes = [d for p in ep["plans"] for d in dialogues(p)]
    sans = [d["texte"][:30] for d in lignes if "source" not in d]
    ok(not sans, "Chaque réplique indique sa source (liste de rN, [] si ajoutée)", "; ".join(sans) or "oui")
    vise = {f"r{i}" for i in plage(adapt.get("repliques", f"1-{len(src)}"))}
    pris = {r for d in lignes for r in d.get("source") or []}
    coupees = set(adapt.get("coupees", []))
    couv = len((pris | coupees) & vise) / max(1, len(vise))
    manquent = sorted(vise - pris - coupees, key=lambda x: int(x[1:]))
    ok(couv >= 0.9, "Fidélité : 90 %+ des répliques source reprises (ou coupées exprès dans adaptation.coupees)",
       f"{round(100 * couv)} %" + (f", oubliées : {', '.join(manquent)}" if manquent else ""))
    ajouts = sum(1 for d in lignes if d.get("source") == [])
    ok(ajouts <= max(2, len(lignes) * 0.3), "Ajouts limités (30 % max de répliques inventées)",
       f"{ajouts}/{len(lignes)}", "À VOIR")
    copies = []
    for d in lignes:
        orig = " ".join(src.get(r, "") for r in d.get("source") or [])
        if orig and len(norm(d["texte"]).split()) > 3:
            ratio = SequenceMatcher(None, norm(d["texte"]), norm(orig)).ratio()
            if ratio >= 0.7:
                copies.append(f"« {d['texte'][:40]} » ≈ {', '.join(d['source'])} ({round(100 * ratio)} %)")
    ok(not copies, "Anti-copier-coller : aucune réplique à 70 %+ identique à l'original", "; ".join(copies) or "oui")
    interdits = [x for x in dis.get("noms_a_eviter", []) if len(x) > 2]
    for pe in dis.get("personnages", []):  # prénoms seulement (mots à majuscule), pas « (le patron) »
        nom = pe.get("nom_source", "")
        if not nom.startswith("("):
            interdits += [w for w in re.split(r"[ /,]+", nom) if len(w) > 2 and w[:1].isupper() and w not in ("Les", "Le", "La")]
    textes = " ".join([d["texte"] for d in lignes] + [str(ep.get(k, "")) for k in ("titre", "legende", "titre_couverture")]
                      + [str(p.get("texte_decor", "")) for p in ep["plans"]])
    t = " " + norm(textes) + " "
    repris = sorted({x for x in interdits if f" {norm(x)} " in t})
    ok(not repris, "Aucun nom propre de la source (personnages, lieux, marques)", ", ".join(repris) or "oui")
    persos_src = {pe.get("animal_ou_fruit", "").lower() for pe in dis.get("personnages", [])} - {""}
    nos = {x.get("animal", "").lower() for x in b.persos.values()}
    ok(not (persos_src & nos), "Espèces différentes de la source", ", ".join(persos_src & nos) or "oui", "À VOIR")
    return res


def main():
    res = verifier(*args_projet(sys.argv[1:]))
    for niv, regle, mes in res:
        print(f"{niv:8} {regle} — {mes}")
    ech = sum(1 for r in res if r[0] == "ÉCHEC")
    av = sum(1 for r in res if r[0] == "À VOIR")
    print(f"\n{ech} échec(s), {av} à voir, {sum(1 for r in res if r[0] == 'OK')} OK")
    sys.exit(1 if ech else 0)


if __name__ == "__main__":
    main()
