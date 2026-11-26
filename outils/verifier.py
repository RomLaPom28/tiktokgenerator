"""Contrôle qualité d'un épisode AVANT de produire le pack : technique d'un côté, éditorial de l'autre.

Usage : python outils/verifier.py <projet> [epNNN] [--detail]   (ep001 par défaut)

Chaque contrôle est déclaré dans bible/controles.json avec sa nature :
- technique   → ÉCHEC, bloquant (pack.py refuse) : ce qui casse les prompts, Grok, ChatGPT ou la conformité TikTok ;
- editorial   → À VOIR, recommandation sur l'histoire, la rétention ou la publication ;
- preference  → À VOIR, préférence de réalisation (rythme, variété), informative.
Une recommandation écartée volontairement (episode.json "choix_creatifs": {"<id>": "pourquoi"}) s'affiche CHOIX.
La grille narrative et le Script Doctor (outils/doctor.py, revue.json) donnent le verdict éditorial, séparé du
verdict technique : un épisode peut être techniquement valide et éditorialement faible, le rapport le dit.
Code de sortie : 1 s'il y a au moins une erreur technique, sinon 0.
"""
import json
import re
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from itertools import groupby
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doctor  # noqa: E402
from commun import ANALYSES, args_projet, compat_plan, dialogues, duree_plan, lire_json  # noqa: E402

PROCHES = {"TGP", "GP", "PR"}
NIVEAU = {"technique": "ÉCHEC", "editorial": "À VOIR", "preference": "À VOIR"}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).strip()


def historique(b, numero):
    f = b.episodes / "historique.json"
    if not f.exists():
        return []
    return sorted((e for e in lire_json(f) if e["numero"] < numero), key=lambda e: e["numero"])


class Rapport:
    """Collecte les contrôles. Chaque entrée : {id, nature, niveau, regle, mesure, raison?}."""

    def __init__(self, choix=None):
        self.reg = doctor.controles()["regles"]
        self.choix = choix or {}
        self.res = []

    def p(self, rid, cle, defaut=None):
        return self.reg[rid].get(cle, defaut)

    def ok(self, rid, cond, mesure, regle=None):
        r = self.reg[rid]  # KeyError = contrôle non déclaré dans controles.json (voulu : registre complet)
        nature = r["nature"]
        if cond:
            niveau = "OK"
        elif nature != "technique" and self.choix.get(rid):
            niveau = "CHOIX"
        else:
            niveau = NIVEAU[nature]
        self.res.append({"id": rid, "nature": nature, "niveau": niveau, "regle": regle or r["nom"],
                         "mesure": mesure, "raison": self.choix.get(rid) if niveau == "CHOIX" else None})

    def echec(self, rid, mesure):
        self.ok(rid, False, mesure)


# ====================================================================== chargement (JSON, champs)
def charger(projet, nom):
    """(Bible, episode) ou (None, rapport d'erreurs) si un fichier est illisible ou incomplet."""
    from bible import Bible
    rap = Rapport()
    try:
        b = Bible(projet)
    except SystemExit:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as e:
        rap.echec("json_valide", f"projet {projet} : personnages.json, lieux.json ou projet.json illisible ({type(e).__name__}: {e})")
        return None, None, rap
    f = b.episodes / nom / "episode.json"
    if not f.exists():
        rap.echec("json_valide", f"{f.as_posix()} introuvable")
        return b, None, rap
    try:
        ep = lire_json(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        rap.echec("json_valide", f"episode.json invalide : {e}")
        return b, None, rap
    rap.ok("json_valide", True, "oui")
    rap.choix = ep.get("choix_creatifs") or {}
    manque = [k for k in ("numero", "titre", "plans") if k not in ep]
    if not manque and (not isinstance(ep["plans"], list) or not ep["plans"]):
        manque.append("plans (liste vide)")
    for i, p in enumerate(ep.get("plans") or []):
        if not isinstance(p, dict):
            manque.append(f"plans[{i}] n'est pas un objet")
            continue
        for k in ("n", "lieu", "lumiere", "cadrage", "camera", "persos"):
            if k not in p:
                manque.append(f"plan {p.get('n', i + 1)}.{k}")
        for j, d in enumerate(p.get("dialogues") or []):
            manque += [f"plan {p.get('n', i + 1)} dialogues[{j}].{k}" for k in ("t", "parle", "texte") if not d.get(k)]
        for j, e in enumerate(p.get("timeline") or []):
            manque += [f"plan {p.get('n', i + 1)} timeline[{j}].{k}" for k in ("t", "action") if not e.get(k)]
        for j, x in enumerate(p.get("persos") or []):
            if not isinstance(x, dict) or "id" not in x:
                manque.append(f"plan {p.get('n', i + 1)} persos[{j}].id")
    rap.ok("champs_obligatoires", not manque, "; ".join(manque[:12]) + (" …" if len(manque) > 12 else "") or "oui")
    return b, (None if manque else ep), rap


# ====================================================================== contrôles
def verifier(projet, nom):
    """Liste des contrôles (dicts) + infos pour le rapport final."""
    b, ep, rap = charger(projet, nom)
    if ep is None:
        return rap.res, {"b": b, "ep": None}
    ok, P = rap.ok, rap.p
    bruts = ep["plans"]
    plans = [compat_plan(p) for p in bruts]
    hist = historique(b, ep["numero"]) if b.serie else []
    r = b.real
    adapt = ep.get("adaptation") or b.projet.get("adaptation")
    v3 = (b.projet.get("creer") or 0) >= 3
    # Épisodes écrits avant les règles « moteur + fonctions » (la-ferme ep001-002, faux-joueur-district) :
    # ces deux champs y deviennent des recommandations. Tout nouvel épisode porte "controle": 2 (skills) et y est soumis.
    ancien = not (v3 or adapt or (ep.get("controle") or 0) >= 2 or ep.get("moteur"))

    # ---------- workflow ----------
    if v3 and not adapt:
        h = b.dossier / "histoire.json"
        hist_ok = h.exists() and bool(lire_json(h).get("choix"))
        ok("histoire_validee", hist_ok, "oui" if hist_ok else "absente ou non validée : refaire l'étape B")

    # ---------- structure et références ----------
    nums = [p.get("n") for p in bruts]
    ok("numerotation_plans", nums == list(range(1, len(bruts) + 1)), nums if nums != list(range(1, len(bruts) + 1)) else "oui")
    ok("nb_plans_bornes", P("nb_plans_bornes", "min") <= len(plans) <= P("nb_plans_bornes", "max"), len(plans))
    if not adapt:
        ok("plans_conseilles", P("plans_conseilles", "min") <= len(plans) <= P("plans_conseilles", "max"), len(plans))
    err = {"codes_realisation": [], "lieux_existants": [], "persos_existants": [], "tenues_existantes": [],
           "jeu_present": [], "parleur_present": [], "mouvement_present": []}
    for p in plans:
        if p.get("lieu") not in b.lieux:
            err["lieux_existants"].append(f"plan {p['n']} lieu={p.get('lieu')}")
        for champ, table in (("lumiere", r["lumieres"]), ("cadrage", r["cadrages"]), ("angle", r["angles"]), ("camera", r["cameras"])):
            if p.get(champ, "face" if champ == "angle" else None) not in table:
                err["codes_realisation"].append(f"plan {p['n']} {champ}={p.get(champ)}")
        fin = p.get("fin") or {}
        for champ, table in (("cadrage", r["cadrages"]), ("angle", r["angles"])):
            if champ in fin and fin[champ] not in table:
                err["codes_realisation"].append(f"plan {p['n']} fin.{champ}={fin[champ]}")
        for pe in p.get("persos", []) + fin.get("persos", []):
            if pe["id"] not in b.persos:
                err["persos_existants"].append(f"plan {p['n']} {pe['id']}")
            elif pe.get("tenue", "base") not in b.persos[pe["id"]]["tenues"]:
                err["tenues_existantes"].append(f"plan {p['n']} {pe['id']}.{pe.get('tenue')}")
            if not pe.get("jeu"):
                err["jeu_present"].append(f"plan {p['n']} {pe['id']}")
        presents = {x["id"] for x in p.get("persos", [])} | {x["id"] for x in fin.get("persos", [])}
        for d in dialogues(p):
            if d.get("parle") not in b.persos:
                err["persos_existants"].append(f"plan {p['n']} parle={d.get('parle')}")
            elif d.get("parle") not in presents and not d.get("hors_champ"):
                err["parleur_present"].append(f"plan {p['n']} {d.get('parle')}")
        if not p.get("mouvement") and not p.get("timeline"):
            err["mouvement_present"].append(f"plan {p['n']}")
    for rid, e in err.items():
        ok(rid, not e, "; ".join(e) or "oui")

    tous = {pe["id"] for p in plans for pe in p["persos"] + (p.get("fin") or {}).get("persos", [])}
    ok("nb_persos_max", len(tous) <= P("nb_persos_max", "max"), len(tous))
    vu, conflits = {}, []
    for p in plans:
        for pe in p["persos"]:
            k = (pe["id"], p["lieu"])
            t = pe.get("tenue", "base")
            if k in vu and vu[k] != t and "flashback" not in ep.get("format", ""):
                conflits.append(f"{pe['id']} plan {p['n']}")
            vu.setdefault(k, t)
    ok("tenues_coherentes", not conflits, ", ".join(conflits) or "oui")

    # ---------- durées et timecodes ----------
    durees = [duree_plan(p) for p in plans]
    ok("durees_grok", all(d in P("durees_grok", "valeurs") for d in durees), durees)
    sans_fin = [p["n"] for p in plans if duree_plan(p) == 10 and not p.get("fin")]
    ok("image_fin_10s", not sans_fin, sans_fin or "oui")
    hors, debit, lents, chevauche = [], [], [], []
    vmax = P("debit_parle", "max_mots_s")
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
            if x.get("texte") and z > a and len(x["texte"].split()) / (z - a) > vmax + 1e-9:
                debit.append(f"{p['n']}:« {x['texte'][:25]}… » {len(x['texte'].split()) / (z - a):.1f} mots/s")
        if not p.get("muet") and len(p.get("timeline") or []) < -(-d // P("temps_forts", "toutes_s")):
            lents.append(f"{p['n']}:{len(p.get('timeline') or [])}/{-(-d // P('temps_forts', 'toutes_s'))}")
        try:
            iv = sorted((float(str(x["t"]).split("-")[0]), float(str(x["t"]).split("-")[-1])) for x in dialogues(p))
            chevauche += [f"{p['n']}:{b2[0]}" for a2, b2 in zip(iv, iv[1:]) if b2[0] < a2[1] - 0.05]
        except ValueError:
            pass
    ok("timecodes", not hors, ", ".join(hors) or "oui")
    ok("debit_parle", not debit, "; ".join(debit) or "oui")
    ok("parole_superposee", not chevauche, ", ".join(chevauche) or "oui")
    ok("durees_variees", durees.count(10) >= P("durees_variees", "min_10") and durees.count(6) >= P("durees_variees", "min_6"),
       f"{durees.count(6)}×6 s, {durees.count(10)}×10 s")
    tot = sum(durees)
    ok("rush_total", P("rush_total", "min") <= tot <= P("rush_total", "max"), f"{tot} s")
    ok("temps_forts", not lents, ", ".join(lents) or "oui")

    # ---------- moteur et fonctions des répliques ----------
    mo = ep.get("moteur") or {}
    socle = {"desir": ("desir",), "conflit": ("conflit", "injustice"), "antagoniste": ("antagoniste", "obstacle"),
             "enjeu": ("enjeu", "enjeu_chiffre"), "payoff": ("payoff", "fin")}
    manque = [k for k, alts in socle.items() if not any(mo.get(a) for a in alts)]
    fonctions = Counter(d.get("fonction") or "?" for p in bruts for d in dialogues(p))
    inval = fonctions.get("?", 0) + fonctions.get("info", 0)  # liste ouverte : « mensonge » est une vraie fonction
    if ancien:  # mêmes mesures, signalées sans bloquer (épisodes déjà produits)
        rap.res.append({"id": "moteur_socle", "nature": "editorial", "niveau": "OK" if not manque else "À VOIR",
                        "regle": rap.reg["moteur_socle"]["nom"] + " (ancien épisode)", "mesure": manque or "oui", "raison": None})
        rap.res.append({"id": "fonction_repliques", "nature": "editorial", "niveau": "OK" if not inval else "À VOIR",
                        "regle": rap.reg["fonction_repliques"]["nom"] + " (ancien épisode)", "mesure": dict(fonctions), "raison": None})
    else:
        ok("moteur_socle", not manque, manque or "oui")
        ok("fonction_repliques", not inval, dict(fonctions))

    # ---------- hook ----------
    d1 = dialogues(bruts[0])
    p1 = plans[0]
    muet1 = not d1 and bruts[0].get("muet")
    if muet1:
        ok("premiere_replique_tot", True, f"plan 1 muet volontaire : {bruts[0]['muet']}")
    else:
        ok("premiere_replique_tot", bool(d1) and doctor.debut(d1[0]["t"]) <= P("premiere_replique_tot", "max_s"),
           d1[0]["t"] if d1 else "—")
        h1 = d1[0]["texte"] if d1 else ""
        ok("hook_court", bool(h1) and len(h1.split()) <= P("hook_court", "max_mots"), h1 or "—")
    ok("plan1_serre", p1["cadrage"] in PROCHES | {"ECRAN", "INSERT"}, p1["cadrage"])
    ta = ep.get("texte_accroche", "")
    ok("texte_accroche", bool(ta) and len(ta.split()) <= P("texte_accroche", "max_mots"), ta or "—")
    ok("hooks_alternatifs", len(ep.get("hooks_alternatifs", [])) >= P("hooks_alternatifs", "min"), len(ep.get("hooks_alternatifs", [])))
    ok("types_declares", ep.get("accroche_type") in r["accroches"] and ep.get("cliff_type") in r["cliffhangers"],
       f"accroche={ep.get('accroche_type')}, fin={ep.get('cliff_type')}")

    # ---------- dialogues ----------
    maxi = P("replique_mots", "max_mots_adaptation") if adapt else P("replique_mots", "max_mots")
    longs = [f"{p['n']}:{len(d['texte'].split())}" for p in plans for d in dialogues(p) if not 1 <= len(d["texte"].split()) <= maxi]
    ok("replique_mots", not longs, ", ".join(longs) or "oui", f"Répliques de 1 à {maxi} mots")
    parleurs = [d["parle"] for p in plans for d in dialogues(p)]
    suite = max((sum(1 for _ in g) for _, g in groupby(parleurs)), default=0)
    ok("meme_parleur_affilee", suite <= P("meme_parleur_affilee", "max"), suite)
    sans_raison = [p["n"] for p in bruts if not dialogues(p) and not p.get("muet")]
    ok("muet_justifie", not sans_raison, sans_raison or "oui")
    n_muets = sum(1 for p in bruts if not dialogues(p))
    ok("muets_minoritaires", n_muets <= max(2, len(plans) // 3), n_muets)

    # ---------- préférences de rythme (outils, jamais des quotas) ----------
    pingpong = sum(1 for p in plans if len({d["parle"] for d in dialogues(p)}) >= 2)
    ok("pingpong", pingpong >= P("pingpong", "min"), pingpong)
    clash = sum(1 for p in bruts for a_, b_ in zip(dialogues(p), dialogues(p)[1:])
                if a_.get("fonction") in ("attaque", "menace") and b_.get("fonction") == "riposte" and a_["parle"] != b_["parle"])
    ok("clashs", clash >= P("clashs", "min"), clash)
    if mo.get("callback"):
        cb = norm(mo["callback"])
        n_cb = sum(1 for p in bruts for d in dialogues(p) if cb and cb in norm(d["texte"]))
        ok("callback", n_cb >= P("callback", "min"), n_cb)
    mous, trous = [], []
    for p in bruts:
        ds = dialogues(p)
        if not ds or p.get("muet"):  # un silence déclaré (muet) est une intention, pas un trou
            continue
        try:
            iv = sorted((float(str(d["t"]).split("-")[0]), float(str(d["t"]).split("-")[-1])) for d in ds)
        except ValueError:
            continue
        parle = sum(z - a for a, z in iv)
        if parle / duree_plan(p) < P("parole_part", "min"):
            mous.append(f"{p['n']}:{int(100 * parle / duree_plan(p))}%")
        gaps = [iv[0][0]] + [b2[0] - a2[1] for a2, b2 in zip(iv, iv[1:])]
        if max(gaps) > P("silence_max", "max_s"):
            trous.append(f"{p['n']}:{max(gaps):.1f}s")
    ok("parole_part", not mous, ", ".join(mous) or "oui")
    ok("silence_max", not trous, ", ".join(trous) or "oui")
    ok("trois_parleurs", len(set(parleurs)) >= P("trois_parleurs", "min"), len(set(parleurs)))
    ok("texte_decor", any(p.get("texte_decor") for p in plans), sum(1 for p in plans if p.get("texte_decor")))
    qm = ep.get("question_milieu") or {}
    ok("question_milieu", bool(qm.get("texte")) and 5 <= int(qm.get("plan", 0) or 0) <= 8,
       f"plan {qm.get('plan')} : {qm.get('texte', '—')}")
    ret = [p["n"] for p in plans if p.get("role") == "retournement"]
    ok("retournements_positions", any(3 <= n <= 6 for n in ret) and any(7 <= n <= 11 for n in ret), ret or "aucun")

    # ---------- fin et publication ----------
    if not b.serie:
        ok("dernier_plan_role", plans[-1].get("role") in ("cliff", "fin", "climax"), plans[-1].get("role"))
    else:
        ok("dernier_plan_role", plans[-1].get("role") == "cliff", plans[-1].get("role"), "Série : dernier plan = cliffhanger")
    ce = ep.get("commentaire_epingle", "")
    ok("commentaire_question", "/" in ce or "?" in ce, ce or "—")
    ok("hashtags_nombre", P("hashtags_nombre", "min") <= len(ep.get("hashtags", [])) <= P("hashtags_nombre", "max"),
       len(ep.get("hashtags", [])))

    # ---------- variété de réalisation ----------
    cad = [p["cadrage"] for p in plans]
    rep = [f"{i + 1}-{i + 2}" for i in range(len(cad) - 1) if cad[i] == cad[i + 1]]
    ok("cadrage_repete", not rep, ", ".join(rep) or "oui")
    ok("cadrages_varies", len(set(cad)) >= P("cadrages_varies", "min"), len(set(cad)))
    ok("plans_serres", sum(c in PROCHES for c in cad) >= P("plans_serres", "min"), sum(c in PROCHES for c in cad))
    cams = [p["camera"] for p in plans]
    ok("cameras_variees", len(set(cams)) >= P("cameras_variees", "min"), len(set(cams)))
    fixes = max((sum(1 for _ in g) for k, g in groupby(cams) if k == "fixe"), default=0)
    ok("fixes_affilee", fixes <= P("fixes_affilee", "max"), fixes)
    ok("zoom_dramatique", cams.count("zoom_dramatique") <= P("zoom_dramatique", "max"), cams.count("zoom_dramatique"))
    ok("angles_varies", len({p.get("angle", "face") for p in plans}) >= P("angles_varies", "min"), len({p.get("angle", "face") for p in plans}))
    lieux = [p["lieu"] for p in plans]
    huis_clos = "huis clos" in ep.get("format", "")
    ok("lieux_varies", len(set(lieux)) >= (1 if huis_clos else P("lieux_varies", "min")), len(set(lieux)))
    ok("lumieres_variees", len({p["lumiere"] for p in plans}) >= P("lumieres_variees", "min"), len({p["lumiere"] for p in plans}))

    # ---------- série ----------
    fils = {f["id"]: f for f in b.saison.get("fils", [])}
    if b.serie:
        av = ep.get("fils_avances", [])
        ok("serie_fil", bool(av) and all(f in fils for f in av), ", ".join(av) or "aucun")
        ok("serie_hashtag_partie", f"#partie{ep['numero']}" in [h.lower() for h in ep.get("hashtags", [])], ep.get("hashtags"))
    rev = [f for f in ep.get("revele", []) if fils.get(f, {}).get("statut") == "cache"]
    ok("serie_un_secret", len(rev) <= 1, ", ".join(rev) or "aucun")
    if hist:
        der = hist[-1]
        ok("serie_format_varie", ep.get("format") not in [h.get("format") for h in hist[-2:]], ep.get("format"))
        ok("serie_accroche_variee", ep.get("accroche_type") not in [h.get("accroche_type") for h in hist[-3:]], ep.get("accroche_type"))
        ok("serie_cliff_varie", ep.get("cliff_type") not in [h.get("cliff_type") for h in hist[-3:]], ep.get("cliff_type"))
        principal = Counter(lieux).most_common(1)[0][0]
        ok("serie_decor_varie", principal != der.get("lieu_principal"), principal)
        ok("serie_centre_varie", ep.get("centre") != der.get("centre"), ep.get("centre"))
        anciennes = {norm(x) for h in hist for x in h.get("repliques", [])}
        doublons = [f"{p['n']}:« {d['texte']} »" for p in bruts for d in dialogues(p) if norm(d["texte"]) in anciennes]
        ok("serie_repliques_neuves", not doublons, doublons or "oui")
        ok("serie_reprend", bool(ep.get("reprend")), ep.get("reprend", "—"))

    # ---------- mécaniques citées (bible/mecaniques.json) ----------
    if ep.get("mecaniques_utilisees"):
        from mecaniques import infos
        inconnues, eviter, a_tester = [], [], []
        for mid in ep["mecaniques_utilisees"]:
            i = infos(mid)
            if i is None:
                inconnues.append(mid)
            elif i[2] == "a_eviter":
                eviter.append(mid)
            elif i[1] == "a_tester":
                a_tester.append(mid)
        ok("mecaniques_connues", not inconnues, inconnues or "oui")
        ok("mecaniques_a_eviter", not eviter, eviter or "oui")
        if a_tester:
            rap.res.append({"id": "mecaniques_a_tester", "nature": "editorial", "niveau": "INFO", "raison": None,
                            "regle": "Mécaniques « à tester » : noter le résultat dans leur tests_ab après publication", "mesure": a_tester})

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
    ok("conformite_rouge", not rouges, "; ".join(rouges) or "oui")
    oranges = [(f"plan {p['n']}", m) for p in plans for m in trouve(p.get("replique", ""), c.get("orange", []))]
    ok("conformite_orange", len(oranges) <= c.get("max_orange", 2), ", ".join(f"{o} « {m} »" for o, m in oranges) or 0,
       f"Mots orange {c.get('max_orange', 2)} max par épisode")
    ok("plan1_sans_gros_mot", not trouve(plans[0].get("replique", ""), c.get("orange", [])), plans[0].get("replique", ""))
    bait = [m for k in ("legende", "commentaire_epingle") for m in trouve(ep.get(k, ""), c.get("appats_interdits", []))]
    bait += trouve(qm.get("texte", ""), c.get("appats_interdits", []))
    ok("appats_interdits", not bait, ", ".join(bait) or "oui")

    fet = Counter()
    for p in plans:
        for pid, x in b.persos.items():
            if (p.get("replique") and x.get("replique_fetiche") and norm(x["replique_fetiche"]) in norm(p["replique"])
                    and norm(x["replique_fetiche"]) != norm(mo.get("callback", ""))):
                fet[pid] += 1
    ok("fetiche_max", max(fet.values(), default=0) <= P("fetiche_max", "max"), dict(fet) or 0)

    if adapt:
        verifier_adaptation(rap, b, ep, adapt)

    # ---------- compatibilité pack.py / bible.py : on assemble vraiment chaque prompt ----------
    techniques_ok = not any(x["niveau"] == "ÉCHEC" for x in rap.res)
    if techniques_ok:
        ok("compat_pack", *compat_pack(b, ep))
    else:
        rap.res.append({"id": "compat_pack", "nature": "technique", "niveau": "INFO", "raison": None,
                        "regle": rap.reg["compat_pack"]["nom"], "mesure": "non testé tant que les erreurs ci-dessus restent"})
    return rap.res, {"b": b, "ep": ep}


def compat_pack(b, ep):
    """Assemble en mémoire tout ce que pack.py écrira (sans rien écrire) : (ok, mesure)."""
    from bible import ouverture_chatgpt, prompt_grok, prompt_image, prompt_portrait
    vides, erreurs = [], []
    try:
        ouv, refs = ouverture_chatgpt(b, ep)
        if not ouv.strip():
            vides.append("ouverture")
        for pid in {x["id"] for p in ep["plans"] for x in p["persos"]}:
            if not prompt_portrait(b, pid).strip():
                vides.append(f"portrait {pid}")
    except Exception as e:  # noqa: BLE001
        erreurs.append(f"ouverture : {type(e).__name__} {e}")
    for p in ep["plans"]:
        try:
            if not prompt_image(b, p).strip():
                vides.append(f"image {p['n']}")
            if p.get("fin") and not prompt_image(b, p, fin=True).strip():
                vides.append(f"image fin {p['n']}")
            if not prompt_grok(b, p).strip():
                vides.append(f"vidéo {p['n']}")
        except Exception as e:  # noqa: BLE001
            erreurs.append(f"plan {p['n']} : {type(e).__name__} {e}")
    n = len(ep["plans"]) * 2 + sum(1 for p in ep["plans"] if p.get("fin"))
    return not (vides or erreurs), "; ".join(erreurs + [f"prompt vide : {v}" for v in vides]) or f"oui ({n} prompts images/vidéos)"


def plage(txt):
    """"r1-r32" -> [1..32]."""
    a, _, z = str(txt).replace("r", "").partition("-")
    return list(range(int(a), int(z or a) + 1))


def verifier_adaptation(rap, b, ep, adapt):
    """Fidélité à la source (chaque réplique source est reprise) ET distance (aucune réplique recopiée)."""
    ok = rap.ok
    f = ANALYSES / str(adapt.get("source")) / "dissection.json"
    if not f.exists():
        ok("adaptation_source", False, f"{f} introuvable (lancer /copier)", "Dissection de la source présente")
        return
    dis = lire_json(f)
    src = {x["r"]: x["texte"] for x in dis.get("repliques", [])}
    lignes = [d for p in ep["plans"] for d in dialogues(p)]
    sans = [d["texte"][:30] for d in lignes if "source" not in d]
    ok("adaptation_source", not sans, "; ".join(sans) or "oui")
    vise = {f"r{i}" for i in plage(adapt.get("repliques", f"1-{len(src)}"))}
    pris = {r for d in lignes for r in d.get("source") or []}
    coupees = set(adapt.get("coupees", []))
    couv = len((pris | coupees) & vise) / max(1, len(vise))
    manquent = sorted(vise - pris - coupees, key=lambda x: int(x[1:]))
    ok("adaptation_fidelite", couv >= rap.p("adaptation_fidelite", "min"),
       f"{round(100 * couv)} %" + (f", oubliées : {', '.join(manquent)}" if manquent else ""))
    ajouts = sum(1 for d in lignes if d.get("source") == [])
    ok("adaptation_ajouts", ajouts <= max(2, len(lignes) * rap.p("adaptation_ajouts", "max")), f"{ajouts}/{len(lignes)}")
    copies = []
    for d in lignes:
        orig = " ".join(src.get(r, "") for r in d.get("source") or [])
        if orig and len(norm(d["texte"]).split()) > 3:
            ratio = SequenceMatcher(None, norm(d["texte"]), norm(orig)).ratio()
            if ratio >= rap.p("adaptation_anti_copie", "max"):
                copies.append(f"« {d['texte'][:40]} » ≈ {', '.join(d['source'])} ({round(100 * ratio)} %)")
    ok("adaptation_anti_copie", not copies, "; ".join(copies) or "oui")
    interdits = [x for x in dis.get("noms_a_eviter", []) if len(x) > 2]
    for pe in dis.get("personnages", []):  # prénoms seulement (mots à majuscule), pas « (le patron) »
        nom = pe.get("nom_source", "")
        if not nom.startswith("("):
            interdits += [w for w in re.split(r"[ /,]+", nom) if len(w) > 2 and w[:1].isupper() and w not in ("Les", "Le", "La")]
    textes = " ".join([d["texte"] for d in lignes] + [str(ep.get(k, "")) for k in ("titre", "legende", "titre_couverture")]
                      + [str(p.get("texte_decor", "")) for p in ep["plans"]])
    t = " " + norm(textes) + " "
    repris = sorted({x for x in interdits if f" {norm(x)} " in t})
    ok("adaptation_noms", not repris, ", ".join(repris) or "oui")
    persos_src = {pe.get("animal_ou_fruit", "").lower() for pe in dis.get("personnages", [])} - {""}
    nos = {x.get("animal", "").lower() for x in b.persos.values()}
    ok("adaptation_especes", not (persos_src & nos), ", ".join(persos_src & nos) or "oui")


# ====================================================================== décision finale
def decision(res, ctx, nom):
    """Rassemble technique + éditorial en cinq rubriques et deux verdicts."""
    b, ep = ctx["b"], ctx["ep"]
    d = {"bloquants": [x for x in res if x["niveau"] == "ÉCHEC"],
         "editorial": [x for x in res if x["niveau"] == "À VOIR" and x["nature"] == "editorial"],
         "preferences": [x for x in res if x["niveau"] == "À VOIR" and x["nature"] == "preference"],
         "choix": [x for x in res if x["niveau"] == "CHOIX"],
         "infos": [x for x in res if x["niveau"] == "INFO"],
         "indices": {}, "revue": None, "revue_erreurs": [], "revue_perimee": False,
         "faiblesses_auto": [], "risques": [], "points_forts": [], "verdict": None, "verdict_declare": None}
    if ep is None:
        return d
    d["indices"] = doctor.indices(b, ep)
    d["faiblesses_auto"] = doctor.faiblesses_auto(b, ep, doctor.autres_projets(b))
    d["risques"] = [f"plan {', '.join(map(str, x['plans']))} : {x['constat']}" for x in doctor.risques_grok(b, ep)]
    rv, err, perimee = doctor.lire_revue(b, nom, ep)
    d["revue"], d["revue_erreurs"], d["revue_perimee"] = rv, err, perimee
    if rv is not None and not err:
        d["verdict"] = doctor.verdict(rv)
        d["verdict_declare"] = rv.get("verdict")
        d["points_forts"] = list(rv.get("points_forts", []))
        d["risques"] += [x for x in rv.get("risques_production", []) if x not in d["risques"]]
    return d


def afficher(res, d, ctx, nom, detail=False):
    c = doctor.controles()
    crit = c["grille_narrative"]["criteres"]
    b, ep = ctx["b"], ctx["ep"]
    titre = f"{b.id if b else '?'} {nom}" + (f" · {ep.get('titre')}" if ep else "")
    print(f"══ Contrôle qualité · {titre}\n")

    def ligne(x):
        m = x["mesure"]
        return f"  - {x['regle']} — {m if not isinstance(m, (list, dict)) else json.dumps(m, ensure_ascii=False)}"

    tech = "VALIDE" if not d["bloquants"] else f"BLOQUÉ ({len(d['bloquants'])} erreur(s))"
    v = d["verdict"]
    if ep is None:
        edit = "NON ÉVALUÉ (épisode illisible)"
    elif d["revue"] is None or d["revue_erreurs"]:
        edit = "NON ÉVALUÉ : lancer le Script Doctor (/doctor) — indices automatiques ci-dessous seulement"
    else:
        edit = {"solide": "SOLIDE", "correct": "CORRECT, PERFECTIBLE",
                "faible": "FAIBLE : produisible techniquement, mais l'histoire est à retravailler"}[v]
        if d["revue_perimee"]:
            edit += " (revue PÉRIMÉE : l'épisode a changé depuis, relancer /doctor)"
    print(f"VERDICT TECHNIQUE : {tech}")
    print(f"VERDICT ÉDITORIAL : {edit}")
    if d["verdict_declare"] and v and doctor.ORDRE_VERDICT[d["verdict_declare"]] > doctor.ORDRE_VERDICT[v]:
        print(f"  (le Script Doctor a écrit « {d['verdict_declare']} », la grille dit « {v} » : la grille l'emporte)")
    if not d["bloquants"] and v == "faible":
        print("  → Techniquement valide mais éditorialement faible : ne pas produire sans l'accord de l'utilisateur.")

    print("\n1. ERREURS BLOQUANTES (techniques)")
    for x in d["bloquants"]:
        print(ligne(x))
    if not d["bloquants"]:
        print("  aucune")

    print("\n2. AMÉLIORATIONS RECOMMANDÉES")
    rv = d["revue"] if not d["revue_erreurs"] else None
    if d["revue_erreurs"]:
        print("  Revue du Script Doctor incomplète :")
        for e in d["revue_erreurs"]:
            print(f"    · {e}")
    print("  Grille narrative" + (" (Script Doctor)" if rv else " (indices automatiques, à confirmer par /doctor)") + " :")
    for k, q in crit.items():
        auto, constats = d["indices"].get(k, (None, []))
        if rv:
            g = rv["grille"][k]
            print(f"    · {q} → {doctor.SYMBOLE[g['note']]}" + (f" — {g['constat']}" if g["note"] != "valide" else ""))
            if g["note"] != "valide":
                print(f"        correction : {g['correction']}")
            if auto == "probleme" and g["note"] == "valide":
                print(f"        ⚠ indice automatique contraire : {'; '.join(constats)} (le doctor doit le justifier)")
        else:
            print(f"    · {q} → {doctor.SYMBOLE[auto]}" + (f" — {'; '.join(constats)}" if constats else ""))
    if rv and rv.get("faiblesses"):
        print("  Faiblesses (Script Doctor) :")
        for f in sorted(rv["faiblesses"], key=lambda f: f.get("gravite") != "probleme"):
            tag = "PROBLÈME" if f.get("gravite") == "probleme" else "à améliorer"
            print(f"    · [{tag}] {c['script_doctor']['faiblesses'][f['type']].split(' :')[0]} (plans {f.get('plans') or '—'}) : {f.get('constat', '')}")
            print(f"        correction : {f['correction']}")
    fa = [f for f in d["faiblesses_auto"] if f["type"] != "trop_complexe_grok"]
    if fa:
        print("  Signaux automatiques" + (" (à confronter à la revue)" if rv else "") + " :")
        for f in fa:
            print(f"    · [{f['type']}] plans {f['plans'] or '—'} : {f['constat']}")
    if d["editorial"]:
        print("  Recommandations éditoriales non suivies :")
        for x in d["editorial"]:
            print("  " + ligne(x))
    if d["preferences"]:
        print("  Préférences de réalisation non suivies (informatif : ne corriger que si la scène y gagne,"
              " sinon les déclarer dans choix_creatifs) :")
        for x in d["preferences"]:
            print("  " + ligne(x))

    print("\n3. POINTS FORTS")
    for x in d["points_forts"]:
        print(f"  - {x}")
    if not d["points_forts"]:
        print("  non évalués : c'est le Script Doctor qui les relève (un indice automatique « valide » n'est pas une force)"
              if not rv else "  aucun relevé par le Script Doctor")

    print("\n4. RISQUES DE PRODUCTION")
    for x in d["risques"]:
        print(f"  - {x}")
    if not d["risques"]:
        print("  aucun repéré")

    print("\n5. VERDICT ÉDITORIAL")
    if rv:
        print(f"  {edit}" + (f"\n  {rv.get('resume')}" if rv.get("resume") else ""))
    else:
        print(f"  {edit}")
    if d["choix"]:
        print("\nCHOIX CRÉATIFS ASSUMÉS (choix_creatifs)")
        for x in d["choix"]:
            print(f"  - {x['regle']} — {x['raison']}")
    for x in d["infos"]:
        print(f"\nINFO  {x['regle']} — {x['mesure']}")
    if detail:
        print("\nDÉTAIL DE TOUS LES CONTRÔLES")
        for x in res:
            print(f"{x['niveau']:8} [{x['nature'][:4]}] {x['regle']} — {x['mesure']}")
    n = Counter(x["niveau"] for x in res)
    print(f"\n{n['ÉCHEC']} erreur(s) bloquante(s), {n['À VOIR']} à voir, {n['CHOIX']} choix assumé(s), {n['OK']} OK")


def main():
    projet, nom = args_projet(sys.argv[1:])
    res, ctx = verifier(projet, nom)
    d = decision(res, ctx, nom)
    afficher(res, d, ctx, nom, detail="--detail" in sys.argv)
    sys.exit(1 if d["bloquants"] else 0)


if __name__ == "__main__":
    main()
