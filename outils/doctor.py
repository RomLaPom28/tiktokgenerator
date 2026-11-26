"""Contrôle narratif et Script Doctor : la partie ÉDITORIALE du contrôle qualité.

Usage :
  python3 outils/doctor.py <projet> [epNNN]            indices automatiques (grille + faiblesses + risques Grok)
  python3 outils/doctor.py <projet> [epNNN] --modele   écrit episodes/epNNN/revue.json vide à remplir (s'il n'existe pas)
  python3 outils/doctor.py <projet> [epNNN] --signer   recopie l'empreinte actuelle de l'épisode dans revue.json
                                                       (seulement après avoir relu la revue sur la version corrigée)

Deux sources, jamais confondues :
- les INDICES calculés ici à partir de episode.json : des signaux (« la scène 4 n'a ni dialogue ni intention »),
  utiles mais aveugles au sens ; ils ne décident pas seuls ;
- la REVUE (episodes/epNNN/revue.json) écrite par le Script Doctor (.claude/skills/doctor/SKILL.md), critique
  indépendante qui note la grille (valide · a_ameliorer · probleme) et propose des corrections précises.
Le verdict éditorial vient de la revue ; sans revue il est « non évalué ». Rien ici ne bloque pack.py.
"""
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import BIBLE, args_projet, dialogues, duree_plan, ecrire_json, lire_json  # noqa: E402

NOTES = ("valide", "a_ameliorer", "probleme")
SYMBOLE = {"valide": "valide", "a_ameliorer": "à améliorer", "probleme": "PROBLÈME IMPORTANT", None: "non évalué"}
FORTES = {"attaque", "menace", "revelation", "aveu", "riposte", "promesse"}
PROCHES = {"TGP", "GP", "PR", "ECRAN", "INSERT"}
# Mots qui trahissent l'exposition (« comme tu le sais… ») : le personnage parle au spectateur, pas à l'autre.
EXPLICATIF = ("comme tu le sais", "comme tu sais", "je te rappelle", "tu te souviens", "rappelle toi", "rappelle-toi",
              "laisse moi t expliquer", "je vais t expliquer", "pour rappel", "comme je l ai dit", "tu sais bien que",
              "comme tout le monde sait", "je t explique")
# Ce que Grok anime mal (bible/editorial.json capacites_generation.difficile), cherché dans les actions et le jeu.
GROK_DIFFICILE = {"combat": r"\b(combat|bagarre|se battent|coup de poing|melee)", "poursuite": r"\bpoursui",
                  "foule qui agit": r"\bfoule\b", "transformation": r"\btransform", "eau": r"\bnage",
                  "véhicule": r"\b(voiture|conduit)\b", "explosion": r"\bexplos", "bébé": r"\b(bebe|nourrisson)\b",
                  "geste technique précis": r"\b(jongl|dribbl)"}


def controles():
    return lire_json(BIBLE / "controles.json")


def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def debut(t):
    try:
        return float(str(t).split("-")[0])
    except ValueError:
        return 0.0


def empreinte(ep):
    """Change dès que l'histoire, les plans ou les dialogues changent : une revue d'une autre version est périmée."""
    cle = {k: ep.get(k) for k in ("titre", "moteur", "plans", "texte_accroche", "commentaire_epingle", "fin")}
    return hashlib.sha1(json.dumps(cle, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]


def histoire_validee(b):
    f = b.dossier / "histoire.json"
    if not f.exists():
        return None
    h = lire_json(f)
    return next((v for v in h.get("variantes", []) if v.get("id") == h.get("choix")), None)


# ---------------------------------------------------------------- indices automatiques (grille)
def indices(b, ep):
    """{critère: (note suggérée, [constats])}. Un constat = un fait mesuré, pas un jugement de goût."""
    plans = ep["plans"]
    lignes = [(p["n"], d) for p in plans for d in dialogues(p)]
    mo = ep.get("moteur") or {}
    centre = ep.get("centre")
    # Anciens épisodes : répliques sans fonction ni moteur. Les signaux qui en dépendent deviennent « non mesurable »
    # au lieu de crier au problème : l'absence d'annotation n'est pas une faiblesse d'histoire.
    annote = bool(lignes) and sum(1 for _, d in lignes if d.get("fonction") not in (None, "", "info")) >= 2 * len(lignes) / 3
    moteur = bool(mo)
    out = {}

    def note(n_pb, n_am):
        return "probleme" if n_pb else ("a_ameliorer" if n_am else "valide")

    # hook
    pb, am = [], []
    d1 = dialogues(plans[0])
    if not d1 and not plans[0].get("muet"):
        pb.append("plan 1 sans réplique et sans intention muette déclarée")
    elif d1:
        h = d1[0]
        if debut(h["t"]) > 1.0:
            am.append(f"1re réplique à {debut(h['t'])} s")
        if len(h["texte"].split()) > 12:
            am.append(f"1re réplique de {len(h['texte'].split())} mots")
        if annote and h.get("fonction") == "reaction":
            am.append("le hook est une réaction : on voit l'effet avant la cause")
    if plans[0].get("cadrage") not in PROCHES:
        am.append(f"plan 1 large ({plans[0].get('cadrage')})")
    if not ep.get("texte_accroche"):
        am.append("pas de texte d'accroche à l'écran")
    out["hook"] = (note(pb, am), pb + am)

    # raison de rester : une question ouverte dans les 2 premiers plans
    pb, am = [], []
    tot_debut = sum(duree_plan(p) for p in plans[:2])
    promesses = [d for n, d in lignes if n <= 2 and d.get("fonction") in ("menace", "promesse", "aveu", "revelation", "attaque")]
    if annote and not promesses:
        pb.append(f"aucune menace, promesse, attaque ou révélation dans les {tot_debut} premières secondes")
    if moteur and not (mo.get("enjeu") or mo.get("enjeu_chiffre")):
        am.append("enjeu non déclaré dans moteur")
    out["raison_rester"] = (note(pb, am), pb + am) if (annote or moteur) else (None, ["non mesurable : ni fonctions ni moteur, juger à la lecture"])

    # désir
    pb, am = [], []
    if not mo.get("desir"):
        am.append("désir non déclaré (moteur.desir)")
    if centre:
        part = sum(1 for _, d in lignes if d.get("parle") == centre) / max(1, len(lignes))
        if part < 0.15:
            am.append(f"le personnage central ({centre}) n'a que {round(100 * part)} % des répliques")
    out["desir"] = (note(pb, am), pb + am)

    # conflit
    pb, am = [], []
    if not (mo.get("conflit") or mo.get("injustice")):
        am.append("conflit non déclaré (moteur.conflit)")
    if not (mo.get("antagoniste") or mo.get("obstacle")):
        am.append("ni antagoniste ni obstacle déclaré")
    oppo = sum(1 for _, d in lignes if d.get("fonction") in ("attaque", "menace", "riposte"))
    if annote and oppo == 0:
        pb.append("aucune réplique d'opposition (attaque, menace, riposte) dans tout l'épisode")
    elif annote and oppo < 2:
        am.append(f"une seule réplique d'opposition (attaque, menace, riposte) dans tout l'épisode")
    out["conflit"] = (note(pb, am), pb + am)

    # enjeux qui montent : le milieu doit changer la donne avant le climax
    pb, am = [], []
    roles = [p.get("role") for p in plans]
    if not any(r in ("retournement", "climax") for r in roles):
        am.append("aucun plan retournement ni climax : la situation monte-t-elle ?")
    milieu = plans[len(plans) // 3: 2 * len(plans) // 3]
    if annote and milieu and not any(d.get("fonction") in ("revelation", "menace", "aveu", "promesse") for p in milieu for d in dialogues(p)):
        am.append("aucune révélation, menace ou promesse dans le tiers central")
    out["enjeux_montent"] = (note(pb, am), pb + am)

    # motivations
    pb, am = [], []
    parlent = {d.get("parle") for _, d in lignes} - {None}
    var = histoire_validee(b)
    if var is not None:
        motiv = norm(" ".join(m.get("perso", "") for m in var.get("motivations", [])))
        sans = [pid for pid in parlent if pid in b.persos and norm(b.persos[pid]["nom"]) not in motiv
                and norm(pid) not in motiv and sum(1 for _, d in lignes if d.get("parle") == pid) >= 3]
        if sans:
            am.append(f"pas de motivation dans histoire.json pour {', '.join(sorted(sans))} (3+ répliques)")
    sans_obj = [pid for pid in parlent if pid in b.persos and not b.persos[pid].get("objectif")]
    if sans_obj:
        am.append(f"objectif vide dans personnages.json : {', '.join(sorted(sans_obj))}")
    out["motivations"] = (note(pb, am), pb + am)

    # retournements
    pb, am = [], []
    for p in plans:
        if annote and p.get("role") == "retournement" and not any(d.get("fonction") in ("revelation", "aveu") for d in dialogues(p)) \
                and not p.get("muet"):
            am.append(f"plan {p['n']} « retournement » sans révélation ni aveu : qu'est-ce qui change ?")
    out["retournements"] = (note(pb, am), pb + am)

    # dialogues
    pb, am = [], []
    if lignes:
        sans_f = [n for n, d in lignes if d.get("fonction") in (None, "", "info")]
        if sans_f:
            am.append(f"{len(sans_f)} réplique(s) sans fonction (plans {sorted(set(sans_f))}) : impossible de mesurer ce qu'elles font")
        reac = sum(1 for _, d in lignes if d.get("fonction") == "reaction") / len(lignes)
        if reac > 0.4:
            am.append(f"{round(100 * reac)} % de réactions : le conflit avance-t-il ?")
        expl = [n for n, d in lignes if any(m in norm(d["texte"]) for m in map(norm, EXPLICATIF))]
        if expl:
            am.append(f"tournure explicative plans {sorted(set(expl))}")
    else:
        pb.append("aucun dialogue")
    out["dialogues"] = (note(pb, am), pb + am)

    # scènes visuelles
    pb, am = [], []
    vides = [p["n"] for p in plans if not dialogues(p) and not p.get("muet")]
    if vides:
        am.append(f"plans {vides} sans dialogue et sans intention déclarée")
    if not any(p.get("detail_image") or p.get("texte_decor") for p in plans):
        am.append("aucun détail d'image ni texte de décor : l'image raconte-t-elle quelque chose ?")
    out["scenes_visuelles"] = (note(pb, am), pb + am)

    # climax
    pb, am = [], []
    if not (mo.get("payoff") or mo.get("fin")):
        am.append("payoff non déclaré (moteur.payoff)")
    cl = [p for p in plans if p.get("role") in ("climax", "fin")] or plans[-2:]
    if annote and not any(d.get("fonction") in ("riposte", "revelation", "aveu", "attaque") for p in cl for d in dialogues(p)) \
            and not any(p.get("muet") for p in cl):
        am.append("le climax ne contient ni riposte, ni révélation, ni aveu")
    out["climax"] = (note(pb, am), pb + am)

    # fin
    pb, am = [], []
    ce = ep.get("commentaire_epingle", "")
    if not ("?" in ce or "/" in ce):
        am.append("commentaire épinglé sans question")
    if plans[-1].get("role") not in ("fin", "climax", "cliff"):
        am.append(f"dernier plan de rôle « {plans[-1].get('role')} »")
    der = dialogues(plans[-1])
    if annote and der and der[-1].get("fonction") == "reaction" and len(der) == 1:
        am.append("la vidéo finit sur une simple réaction")
    out["fin"] = (note(pb, am), pb + am)
    return out


# ---------------------------------------------------------------- détecteurs du Script Doctor
def faiblesses_auto(b, ep, autres_projets=None):
    """Faiblesses que le code sait repérer seul. Les autres (prévisible, artificiel…) demandent une lecture."""
    plans, out = ep["plans"], []
    edito = lire_json(BIBLE / "editorial.json")
    sat = {m["id"] for m in edito.get("moteurs_narratifs", []) if m.get("sature")}
    mn = b.projet.get("moteur_narratif")
    if mn in sat:
        out.append({"type": "deja_vu", "plans": [], "constat": f"moteur narratif saturé ({mn}) : l'angle neuf doit se voir dès le hook"})
    for autre in autres_projets or []:
        if mn and autre.get("moteur_narratif") == mn and autre.get("id") != b.id:
            out.append({"type": "deja_vu", "plans": [], "constat": f"même moteur narratif que le projet {autre['id']}"})
    for p in plans:
        for d in dialogues(p):
            if any(norm(m) in norm(d["texte"]) for m in EXPLICATIF):
                out.append({"type": "dialogue_explicatif", "plans": [p["n"]], "constat": f"« {d['texte']} »"})
        if p.get("role") == "retournement" and any(d.get("fonction") for d in dialogues(p)) \
                and not any(d.get("fonction") in ("revelation", "aveu") for d in dialogues(p)) and not p.get("muet"):
            out.append({"type": "retournement_sans_consequence", "plans": [p["n"]],
                        "constat": "plan marqué retournement sans révélation ni aveu"})
        if not dialogues(p) and not p.get("muet"):
            out.append({"type": "scene_inutile", "plans": [p["n"]], "constat": "ni dialogue ni intention muette"})
    if not dialogues(plans[0]) and not plans[0].get("muet"):
        out.append({"type": "hook_faible", "plans": [1], "constat": "plan 1 vide"})
    out += [dict(r, type="trop_complexe_grok") for r in risques_grok(b, ep)]
    return out


def risques_grok(b, ep):
    out = []
    for p in ep["plans"]:
        ds = dialogues(p)
        parl = {d.get("parle") for d in ds}
        if len(p.get("persos", [])) > 3:
            out.append({"plans": [p["n"]], "constat": f"{len(p['persos'])} personnages à l'image : visages moins stables"})
        if len(parl) > 2 and duree_plan(p) <= 6:
            out.append({"plans": [p["n"]], "constat": f"{len(parl)} bouches en {duree_plan(p)} s : synchronisation labiale fragile"})
        if len(ds) >= 5 and duree_plan(p) <= 6:
            out.append({"plans": [p["n"]], "constat": f"{len(ds)} répliques en 6 s"})
        txt = norm(" ".join([str(p.get("mouvement", ""))] + [e.get("action", "") for e in p.get("timeline") or []]
                            + [x.get("jeu", "") for x in p.get("persos", [])]))
        dur = [nom for nom, rx in GROK_DIFFICILE.items() if re.search(rx, txt)]
        if dur:
            out.append({"plans": [p["n"]], "constat": "action difficile pour Grok : " + ", ".join(dur)})
    return out


# ---------------------------------------------------------------- revue du Script Doctor
def chemin_revue(b, nom):
    return b.episodes / nom / "revue.json"


def modele_revue(ep):
    c = controles()
    return {
        "_consigne": "Remplir selon .claude/skills/doctor/SKILL.md. Chercher les faiblesses, ne pas réécrire l'histoire.",
        "empreinte": empreinte(ep), "date": None, "independant": None,
        "grille": {k: {"note": None, "constat": "", "correction": ""} for k in c["grille_narrative"]["criteres"]},
        "faiblesses": [], "points_forts": [], "risques_production": [], "verdict": None, "resume": "",
    }


def lire_revue(b, nom, ep):
    """(revue ou None, [erreurs de forme], périmée?)"""
    f = chemin_revue(b, nom)
    if not f.exists():
        return None, [], False
    try:
        r = lire_json(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, [f"revue.json illisible : {e}"], False
    c = controles()
    crit = c["grille_narrative"]["criteres"]
    types = c["script_doctor"]["faiblesses"]
    err = []
    g = r.get("grille") or {}
    for k in crit:
        x = g.get(k) or {}
        if x.get("note") not in NOTES:
            err.append(f"grille.{k} : note manquante ou invalide ({x.get('note')})")
        elif x["note"] != "valide" and not str(x.get("correction", "")).strip():
            err.append(f"grille.{k} : {x['note']} sans correction précise")
        if x.get("note") and not str(x.get("constat", "")).strip():
            err.append(f"grille.{k} : constat vide (dire ce qu'on a vu, plan à l'appui)")
    for i, f_ in enumerate(r.get("faiblesses", [])):
        if f_.get("type") not in types:
            err.append(f"faiblesses[{i}] : type inconnu {f_.get('type')}")
        if f_.get("gravite") not in c["script_doctor"]["gravites"]:
            err.append(f"faiblesses[{i}] : gravité {f_.get('gravite')} (a_ameliorer ou probleme)")
        if not str(f_.get("correction", "")).strip():
            err.append(f"faiblesses[{i}] : pas de correction")
        elif len(str(f_["correction"])) > 600:
            err.append(f"faiblesses[{i}] : correction trop longue (corriger précisément, ne pas réécrire l'histoire)")
    if r.get("verdict") not in c["script_doctor"]["verdicts"]:
        err.append(f"verdict invalide ({r.get('verdict')})")
    perimee = bool(r.get("empreinte")) and r["empreinte"] != empreinte(ep)
    return r, err, perimee


def verdict(revue):
    """Verdict calculé depuis la grille et les faiblesses (le verdict déclaré ne peut pas être plus indulgent)."""
    if revue is None:
        return None
    notes = [x.get("note") for x in (revue.get("grille") or {}).values()]
    pb = notes.count("probleme") + sum(1 for f in revue.get("faiblesses", []) if f.get("gravite") == "probleme")
    am = notes.count("a_ameliorer") + sum(1 for f in revue.get("faiblesses", []) if f.get("gravite") == "a_ameliorer")
    return "faible" if pb else ("correct" if am >= 3 else "solide")


ORDRE_VERDICT = {"faible": 0, "correct": 1, "solide": 2}


def autres_projets(b):
    out = []
    for f in sorted(b.dossier.parent.glob("*/projet.json")):
        try:
            out.append(lire_json(f))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    return out


def main():
    from bible import Bible
    projet, nom = args_projet(sys.argv[1:])
    b = Bible(projet)
    ep = lire_json(b.episodes / nom / "episode.json")
    c = controles()
    if "--modele" in sys.argv:
        f = chemin_revue(b, nom)
        if f.exists():
            raise SystemExit(f"{f} existe déjà (ne pas écraser une revue).")
        ecrire_json(f, modele_revue(ep))
        print(f"Modèle écrit : {f.as_posix()}")
        return
    if "--signer" in sys.argv:
        f = chemin_revue(b, nom)
        r = lire_json(f)
        r["empreinte"] = empreinte(ep)
        ecrire_json(f, r)
        print(f"Empreinte mise à jour : {r['empreinte']}")
        return
    print(f"# Indices automatiques · {b.id} {nom} (empreinte {empreinte(ep)})\n")
    print("Signaux mesurés dans episode.json : ils orientent la lecture, ils ne la remplacent pas.\n")
    for k, (n, cs) in indices(b, ep).items():
        print(f"- {c['grille_narrative']['criteres'][k]} → {SYMBOLE[n]}" + ("".join(f"\n    · {x}" for x in cs)))
    fa = faiblesses_auto(b, ep, autres_projets(b))
    print("\n# Faiblesses repérées automatiquement")
    for f in fa or [{"type": "—", "plans": [], "constat": "aucune (les faiblesses de sens restent à chercher à la lecture)"}]:
        print(f"- [{f['type']}] plans {f['plans'] or '—'} : {f['constat']}")


if __name__ == "__main__":
    main()
