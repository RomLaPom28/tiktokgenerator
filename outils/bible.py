"""Charge un projet (projets/<id>) et assemble les prompts ChatGPT / Grok à partir des codes d'un épisode.

Projet = projet.json (type unique|serie), personnages.json, lieux.json, saison.json (série), episodes/.
Commun à tous les projets (bible/) : realisation.json, conformite.json.

Les descriptions des personnages (ADN, tenue, voix) et des lieux sont recopiées MOT POUR MOT
depuis la bible : c'est ce qui garde les personnages identiques d'un plan et d'un épisode à l'autre.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import BIBLE, PROJETS, lire_json  # noqa: E402


class Bible:
    def __init__(self, projet):
        d = PROJETS / projet
        if not (d / "projet.json").exists():
            dispo = ", ".join(sorted(x.name for x in PROJETS.iterdir() if x.is_dir())) if PROJETS.exists() else "aucun"
            raise SystemExit(f"Projet inconnu : {projet} (projets : {dispo})")
        self.id = projet
        self.dossier = d
        self.episodes = d / "episodes"
        self.projet = lire_json(d / "projet.json")
        self.serie = self.projet.get("type") == "serie"
        p = lire_json(d / "personnages.json")
        self.style = p["style"]
        self.persos = {x["id"]: x for x in p["personnages"]}
        self.ordre = [x["id"] for x in p["personnages"]]
        self.lieux = {x["id"]: x for x in lire_json(d / "lieux.json")["lieux"]}
        f = d / "saison.json"
        self.saison = lire_json(f) if f.exists() else {"fils": []}
        self.real = lire_json(BIBLE / "realisation.json")
        f = BIBLE / "conformite.json"
        self.conf = lire_json(f) if f.exists() else {"rouge": {}, "orange": [], "max_orange": 2, "appats_interdits": []}

    def nom(self, pid):
        return self.persos[pid]["nom"]

    def tenue(self, pid, t):
        return self.persos[pid]["tenues"].get(t or "base", self.persos[pid]["tenues"]["base"])


def _phrase(s):
    s = (s or "").strip()
    return s[0].upper() + s[1:] if s else s


QUALITE_IMAGE = ("Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon "
                 "(tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles "
                 "en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, "
                 "contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux.")

REGLES_GROK = ("Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), "
               "mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, "
               "lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du "
               "visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.")


def _texte(plan):
    if plan.get("texte_decor"):
        return (f"Seul texte visible, écrit lisiblement et sans faute dans le décor : {plan['texte_decor']}. "
                "Aucun sous-titre, aucune bulle, aucun vrai logo.")
    return "Aucun texte, aucun sous-titre, aucune bulle, aucun logo."


def _persos(b, persos):
    return [f"{b.persos[p['id']]['adn']}, {b.tenue(p['id'], p.get('tenue'))} : {p['jeu']}." for p in persos]


def prompt_image(b, plan, fin=False):
    """Image de début du plan (ou image de fin si fin=True et plan['fin'] existe)."""
    r = b.real
    lieu = b.lieux[plan["lieu"]]
    src = plan.get("fin", {}) if fin else plan
    cadrage = src.get("cadrage", plan["cadrage"])
    angle = src.get("angle", plan.get("angle", "face"))
    tenues = {p["id"]: p.get("tenue") for p in plan["persos"]}
    persos = [dict(p, tenue=p.get("tenue", tenues.get(p["id"]))) for p in src.get("persos", plan["persos"])]
    titre = f"Image {plan['n']}{' FIN (dernière image du plan, quelques secondes plus tard)' if fin else ''}"
    morceaux = [
        f"{titre} : {r['cadrages'][cadrage]}, {r['angles'][angle]}.",
        f"Décor : {lieu['desc']}.",
        f"Lumière : {r['lumieres'][plan['lumiere']]}.",
        *_persos(b, persos),
    ]
    if src.get("detail_image"):
        morceaux.append(_phrase(src["detail_image"]).rstrip(".") + ".")
    morceaux += [f"STYLE : {b.style}", QUALITE_IMAGE,
                 "Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de "
                 "référence et les images précédentes. Format vertical 9:16.", _texte(plan)]
    return " ".join(morceaux)


def _debut(t):
    try:
        return float(str(t).split("-")[0])
    except ValueError:
        return 0.0


def _tc(t):
    a, _, z = str(t).partition("-")
    return f"[{a}-{z}s]" if z else f"[{a}s]"


def prompt_grok(b, plan):
    from commun import dialogues, duree_plan
    r = b.real
    lieu = b.lieux[plan["lieu"]]
    d = duree_plan(plan)
    lignes = [f"Vidéo verticale 9:16 de {d} secondes à partir de l'image jointe"
              + (" (l'image de fin jointe est la dernière image à atteindre)" if plan.get("fin") else "")
              + (". Animation 3D cartoon, silence volontaire et tendu : " + _phrase(plan["muet"]).rstrip(".") + "."
                 if plan.get("muet") else ". Animation 3D cartoon, rythme très nerveux, aucun temps mort.")]
    evts = []
    tl = plan.get("timeline") or [{"t": f"0-{d}", "action": plan.get("mouvement", "")}]
    for e in tl:
        x = _phrase(e["action"]).rstrip(".") + "."
        if e.get("camera"):
            x += f" Caméra : {r['cameras'].get(e['camera'], e['camera'])}."
        if e.get("son"):
            x += f" Bruitage : {e['son']}."
        evts.append((_debut(e["t"]), 0, f"{_tc(e['t'])} {x}"))
    for di in dialogues(plan):
        p = b.persos[di["parle"]]
        evts.append((_debut(di["t"]), 1, f"{_tc(di['t'])} {p['nom'].upper()}{' (hors champ)' if di.get('hors_champ') else ''} ({p['voix']}, {di.get('emotion') or 'naturel'}) "
                                         f"dit en français : « {di['texte']} »"))
    if not plan.get("timeline") and plan.get("camera"):
        evts.append((0, -1, f"Caméra : {r['cameras'][plan['camera']]}."))
    lignes += [x for _, _, x in sorted(evts)]
    if not dialogues(plan):
        lignes.append("Personne ne parle : seulement des réactions, des souffles et des bruitages.")
    son = lieu["son"] + (f", {plan['son']}" if plan.get("son") else "")
    lignes.append(f"Ambiance sonore : {son}, bruitages cartoon bien appuyés (whoosh, impacts, chocs).")
    lignes.append(REGLES_GROK)
    return "\n".join(lignes)


def ouverture_chatgpt(b, ep):
    # tenues utilisées par personnage dans l'épisode
    tenues = {}
    for pl in ep["plans"]:
        for p in pl["persos"]:
            tenues.setdefault(p["id"], [])
            t = b.tenue(p["id"], p.get("tenue"))
            if t not in tenues[p["id"]]:
                tenues[p["id"]].append(t)
    fiches = "\n".join(f"- {b.persos[pid]['adn']}. Tenue{'s' if len(t) > 1 else ''} : {' / '.join(t)}."
                       for pid, t in sorted(tenues.items(), key=lambda kv: b.ordre.index(kv[0])))
    refs = [b.persos[pid].get("ref", f"refs/{pid}.png") for pid in tenues]
    return ("Tu vas générer les images d'une vidéo. Toutes les images : format vertical 9:16, même style, "
            "mêmes personnages avec EXACTEMENT les mêmes visages, couleurs et accessoires d'une image à l'autre. "
            "Aucun sous-titre ni bulle ; le seul texte autorisé est celui que je décris dans le décor "
            "(tableau d'affichage, banderole, maillot), écrit sans faute.\n\n"
            f"STYLE : {b.style}\n\n"
            f"PERSONNAGES DE CET ÉPISODE (looks fixes) :\n{fiches}\n\n"
            "Si je joins des images de référence, ce sont ces personnages : respecte-les à la lettre.\n"
            "Je vais t'envoyer \"Image 1 : …\", \"Image 2 : …\". Pour chaque message, génère uniquement l'image "
            "demandée, sans commentaire. Réponds juste OK à ce message."), refs


def prompt_portrait(b, pid):
    """Fiche de référence d'un personnage, à générer une fois et à joindre à l'ouverture ChatGPT."""
    x = b.persos[pid]
    return (f"Fiche de référence personnage : {x['adn']}, {b.tenue(pid, 'base')}. "
            f"Plan en pied de trois quarts face, pose de personnage de film d'animation pleine d'attitude, "
            f"expression typique de son caractère ({x.get('caractere', '')}), fond uni dégradé chaud, lumière studio douce. "
            f"Qualité : personnage de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon, grands yeux "
            f"brillants, silhouette ultra reconnaissable, couleurs saturées, aucun décor ni figurant. "
            f"STYLE : {b.style} Vertical 9:16, aucun texte, aucun logo.")
