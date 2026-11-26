"""Intelligence éditoriale de /creer (v3) : Python seul, marche sur le cloud.

Usage :
    python3 outils/creer.py dossier                  # bible/dossier_editorial.md : ce que disent TOUTES les analyses
    python3 outils/creer.py concepts <fichier.json>  # étape A : contrôle les concepts, calcule scores, preuves, recommandation
    python3 outils/creer.py histoire <projet|fichier.json>  # étape B : contrôle projets/<projet>/histoire.json et l'affiche

Lit : analyses/*/ (via mecaniques.py), bible/mecaniques.json, bible/histoires.json, bible/editorial.json, projets/*/projet.json.
Principes :
- les preuves affichées viennent TOUJOURS des données (analyses codées, banque d'histoires), jamais du texte des concepts ;
  une référence citée à la main qui ne contient pas la mécanique est une erreur bloquante ;
- « plus vue » = dans son propre compte, hors suites : une corrélation, jamais une cause ;
- le score éditorial compare des concepts entre eux, il ne prédit pas des vues.
"""
import argparse
import datetime as dt
import itertools
import statistics as st
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mecaniques as M  # noqa: E402
from commun import BIBLE, PROJETS, STUDIO, ecrire_json, lire_json  # noqa: E402

DOSSIER = BIBLE / "dossier_editorial.md"
EDITO = BIBLE / "editorial.json"
HISTOIRES = BIBLE / "histoires.json"
NIV = {"a_tester": "à tester", "recurrente": "récurrente", "fortement_documentee": "fortement documentée"}
RUB = {"socle": "socle", "a_tester": "à tester", "contexte": "dépend du contexte", "a_eviter": "à éviter"}


# ---------------------------------------------------------------- données
class Base:
    def __init__(self):
        self.registre, self.reg = M.charger_registre()
        self.corpus = [v for v in M.charger_corpus() if v["mec"]]
        self.by_id = {v["id"]: v for v in self.corpus}
        self.edito = lire_json(EDITO)
        self.hist = lire_json(HISTOIRES)
        self.moteurs = {m["id"]: m for m in self.edito["moteurs_narratifs"]}
        self.squelettes = {s["id"]: s for s in self.hist.get("squelettes", [])}
        self.greffes = {g["id"]: g for g in self.hist.get("greffes", [])}
        self.projets = self._projets()

    def _projets(self):
        out = []
        for f in sorted(PROJETS.glob("*/projet.json")):
            try:
                p = lire_json(f)
            except ValueError:
                continue
            out.append(p)
        return sorted(out, key=lambda p: (p.get("cree", ""), p.get("id", "")))

    def indice(self, v):
        return M.metriques(v, self.corpus)["indice_compte"]

    def preuves(self, mid):
        return self.reg[mid].get("preuves") or {}

    def canon(self, mid):
        return M.ALIAS.get(mid)

    def videos_avec(self, *mids):
        return [v for v in self.corpus if all(m in M.ids(v) for m in mids)]

    def cooc(self, a, b):
        vs = self.videos_avec(a, b)
        return {"videos": len(vs), "comptes": len({M.compte(v) for v in vs}),
                "histoires": len({M.ctx(v, "serie") or v["id"] for v in vs}),
                "indice": M.med(self.indice(v) for v in vs if M.fmt_de(v) not in M.HORS_SIGNAL), "ids": [v["id"] for v in vs]}

    def refs(self, mid, n=2):
        """Références tirées des données : les plus vues + une sous la médiane de son compte (limite)."""
        srcs = [self.by_id[s["id"]] for s in self.preuves(mid).get("sources", []) if s["id"] in self.by_id]
        top = srcs[:n]
        bas = sorted((v for v in srcs if self.indice(v) and self.indice(v) < 1 and v not in top), key=self.indice)[:1]
        return top, bas

    def obs_moteur(self, mid):
        """Vidéos d'analyses/ où un moteur narratif est observé (squelettes, greffes, vidéos listés dans editorial.json)."""
        m = self.moteurs.get(mid, {})
        vids = {x["id"] for s in m.get("squelettes", []) for x in self.squelettes.get(s, {}).get("source", [])}
        vids |= {x for g in m.get("greffes", []) for x in self.greffes.get(g, {}).get("source", [])}
        vids |= set(m.get("videos", []))
        comptes = {M.compte(self.by_id[v]) for v in vids if v in self.by_id}
        return vids, comptes

    def moteurs_projets(self):
        return Counter(p.get("moteur_narratif") for p in self.projets if p.get("moteur_narratif"))


def fmt_v(b, v):
    i = b.indice(v)
    return f"{v['id']} ({M.compte(v)}, {M.nb(v['meta'].get('vues'))}{', ×' + M.nb(i) + ' son compte' if i else ''})"


def mecas_utiles(b):
    return [m for m in b.registre["mecaniques"] if m["categorie"] != "format"]


# ---------------------------------------------------------------- dossier éditorial
def dossier(b):
    C = b.corpus
    base_ind = M.med(b.indice(v) for v in C if M.fmt_de(v) not in M.HORS_SIGNAL)
    verif = sum(1 for v in C if v["mec"].get("verifie"))
    L = [f"# Dossier éditorial (généré le {dt.date.today().strftime('%d/%m/%Y')})", "",
         f"> Écrit par `python3 outils/creer.py dossier` depuis {len(C)} vidéos analysées ({len({M.compte(v) for v in C})} comptes, "
         f"{verif} fiches v2 vérifiées), `bible/mecaniques.json`, `bible/histoires.json`, `bible/editorial.json` et `projets/`. "
         "Lu par /creer AVANT de proposer des concepts. Ne pas éditer à la main.",
         "> « ×1,8 son compte » = vues de la vidéo ÷ médiane de son compte. « Plus vue » = corrélation dans un même compte, jamais une cause.",
         f"> Médiane du corpus (hors suites) : ×{M.nb(base_ind)} son compte. Le corpus est le haut des comptes : il manque les échecs.", ""]

    # 1. mécaniques par rubrique
    L += ["## 1. Mécaniques : ce qui est documenté, ce qui est à tester, ce qui dépend du contexte", ""]
    for rub in ("socle", "a_tester", "contexte", "a_eviter"):
        ms = [m for m in b.registre["mecaniques"] if (m.get("preuves") or {}).get("usage") == rub]
        if not ms:
            continue
        L.append(f"### {RUB[rub].capitalize()}")
        for m in sorted(ms, key=lambda m: -(m["preuves"].get("comptes", 0) * 100 + m["preuves"].get("videos", 0))):
            p = m["preuves"]
            top, bas = b.refs(m["id"])
            L.append(f"- **`{m['id']}`** ({m['categorie']}) {m['nom']} — {NIV.get(p['niveau'], p['niveau'])}, "
                     f"{p['videos']} vidéos, {p['comptes']} comptes, {p['histoires']} histoires, {p.get('verifiees', 0)} vérifiées · "
                     f"{M.txt_perf(p['performance'])}.")
            L.append(f"  - Effet : {m.get('effet', '')}")
            if m.get("conditions"):
                L.append(f"  - Conditions : {' '.join(m['conditions'])}")
            for cid in p.get("contradictions", []):
                c = next((x for x in b.registre["contradictions"] if x["id"] == cid), None)
                if c:
                    L.append(f"  - Contradiction « {cid} » → décision : {c.get('decision', '')}")
            vs = [(k, x) for k, x in (p.get("variantes") or {}).items() if x["videos"] >= 2]
            if vs:
                L.append("  - Variantes : " + " ; ".join(
                    f"`{k}` {x['videos']} vid./{x['comptes']} comptes" + (f", ×{M.nb(x['ratio'])} ({x['signal']})" if x.get("ratio") else "")
                    for k, x in vs))
            if top:
                L.append("  - Références : " + " ; ".join(fmt_v(b, v) for v in top)
                         + (f" · limite (présente mais sous la médiane de son compte) : {fmt_v(b, bas[0])}" if bas else ""))
        L.append("")

    # 2. associations
    L += ["## 2. Associations de mécaniques", "",
          "Paires observées ensemble (hors format). « éprouvée » = 2 comptes et 3 histoires ou plus ; « rare » = moins.", ""]
    mu = [m["id"] for m in mecas_utiles(b)]
    paires = []
    for a, c in itertools.combinations(mu, 2):
        x = b.cooc(a, c)
        paires.append((a, c, x))
    vues = sorted((p for p in paires if p[2]["videos"]), key=lambda p: (-p[2]["comptes"], -p[2]["videos"]))
    L += ["| Paire | Vidéos | Comptes | Histoires | Indice médian | Statut |", "|---|---|---|---|---|---|"]
    for a, c, x in vues[:18]:
        statut = "éprouvée" if x["comptes"] >= 2 and x["histoires"] >= 3 else "rare"
        L.append(f"| `{a}` + `{c}` | {x['videos']} | {x['comptes']} | {x['histoires']} | "
                 f"{('×' + M.nb(x['indice'])) if x['indice'] else '—'} | {statut} |")
    jamais = [(a, c) for a, c, x in paires if not x["videos"]
              and all((b.preuves(m).get("usage") in ("socle", "a_tester", "contexte")) for m in (a, c))]
    L += ["", "**Jamais observées ensemble** (terrain d'« association nouvelle », à justifier) : "
          + (", ".join(f"`{a}`+`{c}`" for a, c in jamais) or "aucune"), ""]

    # 3. comparaisons dans un même compte
    L += ["## 3. Comparer deux approches dans un même compte", "",
          "Pour chaque compte : sa vidéo la plus forte et la plus faible du corpus (hors suites), et ce qui les distingue. "
          "Une vidéo moins vue est une information, pas un déchet. Écart d'un seul cas : hypothèse, jamais une règle.", ""]
    par = defaultdict(list)
    for v in C:
        if M.fmt_de(v) not in M.HORS_SIGNAL and b.indice(v):
            par[M.compte(v)].append(v)
    lignes = []
    for cpt, vs in par.items():
        if len(vs) < 2:
            continue
        vs.sort(key=b.indice)
        bas, haut = vs[0], vs[-1]
        if b.indice(haut) / b.indice(bas) < 2:
            continue
        plus, moins = sorted(M.ids(haut) - M.ids(bas)), sorted(M.ids(bas) - M.ids(haut))
        d = lambda v: f"{M.ctx(v, 'domaine')}/{M.ctx(v, 'ton')}/{M.fmt_de(v)}"  # noqa: E731
        lignes.append((b.indice(haut) / b.indice(bas),
                       f"- **{cpt}** : {haut['id']} ×{M.nb(b.indice(haut))} ({d(haut)}) contre {bas['id']} ×{M.nb(b.indice(bas))} ({d(bas)}). "
                       f"Seulement dans la forte : {', '.join(f'`{x}`' for x in plus) or 'rien'} ; seulement dans la faible : "
                       f"{', '.join(f'`{x}`' for x in moins) or 'rien'}."))
    L += [x for _, x in sorted(lignes, reverse=True)] or ["- Aucun compte avec un écart net."]
    L.append("")

    # 4. saturation
    L += ["## 4. Ce qui est déjà trop utilisé", ""]
    mp = b.moteurs_projets()
    fam_sq = Counter(s.get("famille") for s in b.squelettes.values())
    L += ["| Moteur narratif | Vidéos du corpus | Comptes | Nos projets | Statut |", "|---|---|---|---|---|"]
    for m in b.edito["moteurs_narratifs"]:
        vids, cpts = b.obs_moteur(m["id"])
        nous = mp.get(m["id"], 0)
        if m.get("sature"):
            statut = "SATURÉ (décision utilisateur) : 2 concepts max par proposition"
        elif nous >= 2:
            statut = "déjà fait plusieurs fois par nous"
        elif not vids:
            statut = "jamais observé : hypothèse créative"
        elif len(cpts) < 2:
            statut = "observé dans un seul compte : peu exploité"
        else:
            statut = "observé"
        if nous == 1 and not m.get("sature"):
            statut += " · déjà fait une fois par nous"
        L.append(f"| `{m['id']}` {m['nom']} | {len(vids)} | {len(cpts)} | {nous} | {statut} |")
    L += ["", "Nos projets (du plus ancien au plus récent) : "
          + " ; ".join(f"{p['id']} ({p.get('cree', '?')}, {p.get('moteur_narratif', '?')}, {p.get('domaine', '?')})" for p in b.projets), ""]
    doms = Counter(M.ctx(v, "domaine") for v in C)
    tons = Counter(M.ctx(v, "ton") for v in C)
    L.append("Domaines du corpus : " + ", ".join(f"{k} {n}" for k, n in doms.most_common()) + ".")
    L.append("Tons du corpus : " + ", ".join(f"{k} {n}" for k, n in tons.most_common()) + ".")
    L.append("")

    # 5. peu exploité
    L += ["## 5. Angles encore peu exploités", ""]
    rares = [k for k, n in doms.items() if n <= 3]
    nos_doms = Counter(p.get("domaine") for p in b.projets if p.get("domaine"))
    dom_jamais = [d for d in b.edito.get("domaines", {}).get("candidats", []) if not doms.get(d)]
    L.append(f"- Domaines rares dans le corpus (3 vidéos ou moins) : {', '.join(sorted(rares)) or 'aucun'} ; candidats jamais codés (sans preuve) : "
             f"{', '.join(dom_jamais) or 'aucun'}. Nos domaines déjà faits : "
             + (", ".join(f"{k} {n}" for k, n in nos_doms.most_common()) or "non renseignés") + ".")
    seuls = [s for s in b.squelettes.values() if len(s.get("source", [])) == 1]
    L.append("- Squelettes vus une seule fois (forts mais peu exploités) : " + " ; ".join(
        f"`{s['id']}` ({M.nb(s['source'][0]['vues'])})" for s in sorted(seuls, key=lambda s: -s['source'][0]['vues'])) + ".")
    pris = {g for p in b.projets for g in (p.get("remix") or {}).get("greffes", [])}
    libres = [g for g in b.greffes if g not in pris]
    L.append("- Greffes jamais utilisées dans nos projets : " + ", ".join(f"`{g}`" for g in libres) + ".")
    at = [m["id"] for m in b.registre["mecaniques"] if (m.get("preuves") or {}).get("niveau") == "a_tester"]
    L.append(f"- Mécaniques à tester (une par concept au plus, assumée comme test) : {', '.join(f'`{x}`' for x in at) or 'aucune'}.")
    rv = [(k, x) for m in b.registre["mecaniques"] for k, x in ((m.get("preuves") or {}).get("variantes") or {}).items()
          if x["videos"] == 1]
    if rv:
        L.append("- Variantes vues une seule fois : " + ", ".join(f"`{k}`" for k, _ in rv) + ".")
    L.append("")

    # 6. limites
    L += ["## 6. Limites et contradictions (à garder en tête)", "",
          f"- {len(C) - verif} vidéos sur {len(C)} ont un codage rétro (fiches v1, `verifie: false`) : les comptes de mécaniques sont approximatifs.",
          "- Aucune mécanique n'est fortement documentée. Aucune n'a de test A/B : rien n'est une cause démontrée.",
          "- Les suites font 30 à 70 % des vues de leur partie 1 : comparer une suite à une vidéo unique n'a pas de sens."]
    for c in b.registre["contradictions"]:
        L.append(f"- **{c['question']}** → {c.get('decision', '')}" + (f" Limites : {c['limites']}" if c.get("limites") else ""))
    L.append("")
    for m in b.edito["moteurs_narratifs"]:  # références de editorial.json vers histoires.json et analyses/
        for x in m.get("squelettes", []):
            if x not in b.squelettes:
                print(f"attention : moteur {m['id']} cite un squelette inconnu « {x} »")
        for x in m.get("greffes", []):
            if x not in b.greffes:
                print(f"attention : moteur {m['id']} cite une greffe inconnue « {x} »")
        for x in m.get("videos", []):
            if x not in b.by_id:
                print(f"attention : moteur {m['id']} cite une vidéo absente de analyses/ « {x} »")
    orphelins = [s_ for s_ in b.squelettes if not any(s_ in m.get("squelettes", []) for m in b.edito["moteurs_narratifs"])]
    if orphelins:
        print("attention : squelettes sans moteur narratif dans editorial.json : " + ", ".join(orphelins))
    DOSSIER.write_text("\n".join(L), encoding="utf-8")
    print(f"{DOSSIER.relative_to(STUDIO)} écrit : {len(C)} vidéos, {len(b.reg)} mécaniques, {len(vues)} paires observées, "
          f"{len(jamais)} paires jamais observées, {len(b.projets)} projets.")


# ---------------------------------------------------------------- étape A : concepts
CHAMPS = ("titre", "pitch", "hook", "hook_image", "conflit", "emotion", "curiosite", "retournement", "fin", "debat",
          "moteur_narratif", "domaine", "mecaniques", "pourquoi_combinaison", "score", "faisabilite")


def analyser_mecas(b, c, res, cid):
    """Statut de chaque mécanique (tiré des données) et classe de la combinaison."""
    lignes, reg_ids, hypo = [], [], False
    for x in c.get("mecaniques", []):
        x = {"id": x} if isinstance(x, str) else x
        if x.get("hypothese"):
            hypo = True
            lignes.append(f"  - 🧪 **hypothèse créative** « {x['hypothese']} » : {x.get('role', '')} (aucune preuve dans nos analyses)")
            continue
        mid = b.canon(x.get("id", ""))
        if not mid:
            res.append(("ÉCHEC", f"{cid} : mécanique inconnue « {x.get('id')} » (mettre {{\"hypothese\": \"…\"}} si c'est une idée nouvelle)"))
            continue
        reg_ids.append(mid)
        p = b.preuves(mid)
        for r in x.get("refs", []):
            v = b.by_id.get(str(r))
            if not v:
                res.append(("ÉCHEC", f"{cid} : référence {r} absente de analyses/ (preuve inventée ?)"))
            elif mid not in M.ids(v):
                res.append(("ÉCHEC", f"{cid} : la vidéo {r} n'est pas codée avec `{mid}` (preuve inventée ?)"))
        top, bas = b.refs(mid)
        if p.get("niveau") == "a_tester":
            hypo = True
            etat = (f"🧪 observée {p.get('videos', 0)} fois seulement ({p.get('comptes', 0)} compte{'s' * (p.get('comptes', 0) > 1)}, "
                    f"{p.get('histoires', 0)} histoire{'s' * (p.get('histoires', 0) > 1)}) : à tester")
        else:
            etat = f"✅ observée {p.get('videos')} fois, {p.get('comptes')} comptes ({NIV.get(p.get('niveau'))}, {RUB.get(p.get('usage'))})"
        perf = M.txt_perf(p["performance"]) if p.get("performance") else ""
        ref = "; ".join(fmt_v(b, v) for v in top) + (f" · limite : {fmt_v(b, bas[0])}" if bas else "")
        lignes.append(f"  - `{mid}` {etat} · {perf}{(' — ' + x['role']) if x.get('role') else ''}\n    Réf. : {ref}")
        if p.get("usage") == "contexte":
            dec = [x.get("decision", "") for x in b.registre["contradictions"] if x["id"] in p.get("contradictions", [])]
            res.append(("À VOIR", f"{cid} : `{mid}` dépend du contexte, l'histoire doit respecter : {' '.join(dec) or '; '.join(b.reg[mid].get('conditions', []))}"))
    reg_ids = list(dict.fromkeys(m for m in reg_ids if b.reg[m]["categorie"] != "format"))
    nouvelles, n_paires = [], 0
    for a, z in itertools.combinations(reg_ids, 2):
        n_paires += 1
        x = b.cooc(a, z)
        if x["comptes"] < 2 or x["histoires"] < 3:
            nouvelles.append(f"`{a}`+`{z}` ({x['videos']} vidéo{'s' * (x['videos'] > 1)} ensemble)")
    lignes.insert(0, f"  - Paires éprouvées (2 comptes, 3 histoires) : {n_paires - len(nouvelles)}/{n_paires}")
    moteur_vu = bool(b.obs_moteur(c.get("moteur_narratif"))[0])
    if hypo:
        classe = "hypothèse créative à tester"
    elif nouvelles or not moteur_vu:
        classe = "association nouvelle de mécaniques connues"
        if not moteur_vu:
            nouvelles.append("moteur narratif jamais observé")
    else:
        classe = "combinaison déjà observée plusieurs fois"
    if len(reg_ids) < 2:
        res.append(("ÉCHEC", f"{cid} : au moins 2 mécaniques de la bibliothèque (hors format)"))
    return lignes, classe, nouvelles


def faisabilite(b, f):
    g = b.edito["faisabilite"]
    np_, nd = int(f.get("nb_personnages", 0)), int(f.get("nb_decors", 0))
    sp = g["personnages"].get(str(np_), 5 if np_ <= 3 else 0)
    sd = g["decors"].get(str(nd), 5 if nd <= 2 else 0)
    notes = [f.get("comprehension", 0), f.get("actions", 0), f.get("compat_generation", 0), sp, sd]
    return 4 * sum(notes), {"personnages": sp, "decors": sd}


def concepts(b, chemin):
    f = Path(chemin)
    data = lire_json(f)
    res = []
    cs = data.get("concepts", [])
    dv = b.edito["diversite"]
    sc = b.edito["score_editorial"]["criteres"]
    ok = lambda cond, msg, niv="ÉCHEC": res.append(("OK" if cond else niv, msg))  # noqa: E731
    ok(dv["concepts_min"] <= len(cs) <= dv["concepts_max"], f"{dv['concepts_min']} à {dv['concepts_max']} concepts ({len(cs)})")
    mp = b.moteurs_projets()
    recents = [p.get("moteur_narratif") for p in b.projets[-3:]]
    cartes = []
    for c in cs:
        cid = c.get("id", "?")
        manque = [k for k in CHAMPS if not c.get(k)]
        ok(not manque, f"{cid} : champs remplis" + (f" (manque {', '.join(manque)})" if manque else ""))
        mo = c.get("moteur_narratif")
        ok(mo in b.moteurs, f"{cid} : moteur narratif connu de bible/editorial.json ({mo})")
        ok(c.get("emotion") in b.edito["emotions"], f"{cid} : émotion dominante de la liste ({c.get('emotion')})", "À VOIR")
        s = c.get("score", {})
        hors = [k for k, v in sc.items() if not 0 <= s.get(k, -1) <= v["max"]]
        ok(not hors, f"{cid} : score dans les bornes" + (f" ({', '.join(hors)})" if hors else ""))
        fa = c.get("faisabilite", {})
        bornes = [k for k in ("comprehension", "actions", "compat_generation") if not 1 <= fa.get(k, 0) <= 5]
        ok(not bornes and fa.get("nb_personnages") and fa.get("nb_decors"),
           f"{cid} : faisabilité notée (1-5) avec nb_personnages et nb_decors" + (f" ({', '.join(bornes)})" if bornes else ""))
        ok(int(fa.get("nb_personnages", 0)) <= 6, f"{cid} : 6 personnages max ({fa.get('nb_personnages')})")
        hook_mots = len(str(c.get("hook", "")).split())
        ok(hook_mots <= 14, f"{cid} : réplique ou texte du hook court ({hook_mots} mots)", "À VOIR")
        if b.moteurs.get(mo, {}).get("sature") and s.get("originalite", 0) > 8:
            res.append(("À VOIR", f"{cid} : moteur saturé noté {s.get('originalite')}/15 en originalité : justifier l'angle neuf"))
        if mo in recents:
            res.append(("À VOIR", f"{cid} : moteur déjà utilisé dans un des 3 derniers projets ({mo})"))
        for h in c.get("histoires", []):
            ok(h in b.squelettes or h in b.greffes, f"{cid} : histoire/greffe « {h} » connue de bible/histoires.json")
        lignes, classe, nouvelles = analyser_mecas(b, c, res, cid)
        total = sum(s.get(k, 0) for k in sc)
        fai, auto = faisabilite(b, fa)
        c["calcul"] = {"score": total, "faisabilite": fai, "notes_auto": auto, "preuve": classe, "paires_nouvelles": nouvelles}
        cartes.append((c, lignes))
    mos = [c.get("moteur_narratif") for c in cs]
    dbl = [m for m, n in Counter(mos).items() if n > 1]
    ok(not dbl, "Moteurs narratifs tous différents" + (f" (doublons : {', '.join(dbl)})" if dbl else ""))
    sat = [c["id"] for c in cs if b.moteurs.get(c.get("moteur_narratif"), {}).get("sature")]
    ok(len(sat) <= dv["max_moteurs_satures"],
       f"Moteurs saturés (faux pauvre, test, humiliation-revanche) : {dv['max_moteurs_satures']} max ({len(sat)} : {', '.join(sat) or '—'})")
    em = {c.get("emotion") for c in cs}
    ok(len(em) >= dv["emotions_distinctes_min"], f"Émotions dominantes variées ({len(em)} différentes)")
    do = {c.get("domaine") for c in cs}
    ok(len(do) >= dv["domaines_distincts_min"], f"Domaines variés ({len(do)} différents)", "À VOIR" if data.get("theme") else "ÉCHEC")
    classes = Counter(c["calcul"]["preuve"] for c in cs if "calcul" in c)
    ok(classes.get("combinaison déjà observée plusieurs fois", 0) < len(cs), "Pas seulement des combinaisons déjà vues", "À VOIR")
    ok(classes.get("combinaison déjà observée plusieurs fois", 0) >= 1,
       "Au moins un concept sur une combinaison éprouvée (sinon le lot est entièrement spéculatif)", "À VOIR")
    ok(classes.get("hypothèse créative à tester", 0) <= len(cs) // 2, "Hypothèses créatives : la moitié des concepts au plus", "À VOIR")

    seuil = b.edito["faisabilite"]["seuil_recommandation"]
    faisables = [c for c in cs if "calcul" in c and c["calcul"]["faisabilite"] >= seuil]
    reco = max(faisables, key=lambda c: (c["calcul"]["score"], c["calcul"]["faisabilite"]), default=None)
    ambitieux = max((c for c in cs if "calcul" in c), key=lambda c: c["calcul"]["score"], default=None)
    data["recommande"] = reco["id"] if reco else None
    data["controle"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    ecrire_json(f, data)
    md = rendu_concepts(b, data, cartes, reco, ambitieux, seuil)
    f.with_suffix(".md").write_text(md, encoding="utf-8")
    return res, md


def obs_txt(b, mid):
    vids, cpts = b.obs_moteur(mid)
    nous = b.moteurs_projets().get(mid, 0)
    t = f"observé {len(vids)} vidéo{'s' * (len(vids) > 1)}, {len(cpts)} compte{'s' * (len(cpts) > 1)}" if vids else "jamais observé : hypothèse"
    if b.moteurs.get(mid, {}).get("sature"):
        t += ", saturé"
    return t + (f", déjà fait {nous}× par nous" if nous else "")


def rendu_concepts(b, data, cartes, reco, ambitieux, seuil):
    sc = b.edito["score_editorial"]["criteres"]
    lab = {"hook": "hook", "curiosite": "curiosité", "emotion": "émotion", "originalite": "originalité",
           "discussion": "discussion", "visuel": "visuel"}
    L = [f"# Concepts {data.get('type', '')} du {data.get('date', '')}" + (f" · thème : {data['theme']}" if data.get("theme") else ""), "",
         "> Score éditorial /100 = outil de comparaison entre ces concepts, pas une prédiction de vues. "
         f"Faisabilité /100 : sous {seuil}, jamais recommandé d'office.", ""]
    L += ["| # | Titre | Moteur | Émotion | Score | Faisab. | Preuve |", "|---|---|---|---|---|---|---|"]
    for c, _ in sorted(cartes, key=lambda x: -x[0].get("calcul", {}).get("score", 0)):
        k = c.get("calcul", {})
        L.append(f"| {c['id']} | {c.get('titre')} | {c.get('moteur_narratif')} | {c.get('emotion')} | {k.get('score')} | {k.get('faisabilite')} | {k.get('preuve')} |")
    L.append("")
    for c, lignes in cartes:
        k = c["calcul"]
        s = c["score"]
        fa = c["faisabilite"]
        L += [f"## {c['id']} · {c['titre']} — {k['score']}/100 · faisabilité {k['faisabilite']}/100", "",
              f"**Pitch** : {c['pitch']}",
              f"**Hook** : « {c['hook']} » · image : {c.get('hook_image', '')}",
              f"**Conflit** : {c['conflit']}",
              f"**Émotion dominante** : {c['emotion']} · **Moteur** : {b.moteurs.get(c['moteur_narratif'], {}).get('nom', c['moteur_narratif'])} "
              f"({obs_txt(b, c['moteur_narratif'])}) · **Domaine** : {c['domaine']}",
              f"**Curiosité** : {c['curiosite']}",
              f"**Retournement** : {c['retournement']}",
              f"**Fin** : {c['fin']}",
              f"**Débat** : {c['debat']}",
              f"**Preuve** : {k['preuve']}" + (f" (jamais ou rarement ensemble : {', '.join(k['paires_nouvelles'])})" if k["paires_nouvelles"] else ""),
              "**Mécaniques** :"] + lignes
        if c.get("histoires"):
            L.append("  - Histoires de la banque : " + " ; ".join(
                f"`{h}` ({', '.join(M.nb(x['vues']) for x in b.squelettes[h]['source'])})" if h in b.squelettes else f"greffe `{h}` ({', '.join(b.greffes[h]['source'])})"
                for h in c["histoires"] if h in b.squelettes or h in b.greffes))
        L += [f"**Pourquoi cette combinaison** : {c['pourquoi_combinaison']}",
              f"**Score** : " + " · ".join(f"{lab[x]} {s.get(x)}/{sc[x]['max']}" for x in sc) + (f" — {c['justif_score']}" if c.get("justif_score") else ""),
              f"**Faisabilité** : compréhension {fa.get('comprehension')}/5 · actions {fa.get('actions')}/5 · génération {fa.get('compat_generation')}/5 · "
              f"{fa.get('nb_personnages')} personnages ({k['notes_auto']['personnages']}/5) · {fa.get('nb_decors')} décors ({k['notes_auto']['decors']}/5)"
              + (f" — risques : {'; '.join(fa['risques'])}" if fa.get("risques") else ""), ""]
    if reco:
        L.append(f"**Recommandé : {reco['id']} · {reco['titre']}** (meilleur score parmi les concepts faisables à {seuil}+).")
    if ambitieux and reco and ambitieux["id"] != reco["id"]:
        L.append(f"Plus ambitieux : {ambitieux['id']} · {ambitieux['titre']} ({ambitieux['calcul']['score']}/100) mais faisabilité "
                 f"{ambitieux['calcul']['faisabilite']}/100 : pas recommandé d'office.")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- étape B : histoire
CHAMPS_H = ("nom", "logline", "debut", "conflit", "motivations", "progression", "retournements", "climax", "fin", "emotions")


def histoire(b, projet):
    f = Path(projet) if projet.endswith(".json") else PROJETS / projet / "histoire.json"
    if not f.exists():
        raise SystemExit(f"{f} introuvable")
    h = lire_json(f)
    res = []
    ok = lambda cond, msg, niv="ÉCHEC": res.append(("OK" if cond else niv, msg))  # noqa: E731
    vs = h.get("variantes", [])
    ok(1 <= len(vs) <= 2, f"1 ou 2 variantes ({len(vs)})")
    ok(h.get("moteur_narratif") in b.moteurs, f"Moteur narratif connu ({h.get('moteur_narratif')})")
    for v in vs:
        manque = [k for k in CHAMPS_H if not v.get(k)]
        ok(not manque, f"Variante {v.get('id')} complète" + (f" (manque {', '.join(manque)})" if manque else ""))
        ok(len(v.get("personnages", [])) <= 6, f"Variante {v.get('id')} : 6 personnages max ({len(v.get('personnages', []))})")
        ok(1 <= len(v.get("decors", [])) <= 6, f"Variante {v.get('id')} : 1 à 6 décors ({len(v.get('decors', []))})")
    if len(vs) == 2:
        a, z = vs
        txt = lambda v: " ".join([v.get("conflit", ""), " ".join(v.get("retournements", [])), v.get("climax", ""), v.get("fin", "")])  # noqa: E731
        r = SequenceMatcher(None, txt(a), txt(z)).ratio()
        ok(r < 0.6, f"Les 2 variantes diffèrent vraiment (ressemblance {round(100 * r)} %)")
        ok(bool(a.get("difference") or z.get("difference")), "La différence entre variantes est dite en une phrase", "À VOIR")
    if h.get("choix"):
        ok(h["choix"] in {v.get("id") for v in vs}, f"Choix validé : {h['choix']} ({h.get('valide', 'date ?')})")
    L = [f"# {h.get('titre', projet)} — histoire ({'validée : ' + h['choix'] if h.get('choix') else 'en attente de validation'})", ""]
    for v in vs:
        L += [f"## Variante {v.get('id')} · {v.get('nom')}", "", f"**En une phrase** : {v.get('logline')}",
              f"**Début** : {v.get('debut')}", f"**Conflit** : {v.get('conflit')}", "**Motivations** :"]
        L += [f"- {m.get('perso')} : veut {m.get('veut')}" + (f" ; cache {m['cache']}" if m.get("cache") else "") for m in v.get("motivations", [])]
        L += ["**Progression** :"] + [f"{i}. {x}" for i, x in enumerate(v.get("progression", []), 1)]
        L += ["**Retournements** :"] + [f"- {x}" for x in v.get("retournements", [])]
        L += [f"**Climax** : {v.get('climax')}", f"**Fin** : {v.get('fin')}",
              f"**Émotions** : {' → '.join(v.get('emotions', []))}",
              f"**Casting** : {', '.join(v.get('personnages', []))} · **Décors** : {', '.join(v.get('decors', []))}"]
        if v.get("difference"):
            L.append(f"**Ce qui change vraiment** : {v['difference']}")
        L.append("")
    md = "\n".join(L)
    f.with_suffix(".md").write_text(md, encoding="utf-8")
    return res, md


def imprimer(res):
    for niv, msg in res:
        if niv != "OK":
            print(f"{niv:8} {msg}")
    e = sum(1 for r in res if r[0] == "ÉCHEC")
    print(f"\n{e} échec(s), {sum(1 for r in res if r[0] == 'À VOIR')} à voir, {sum(1 for r in res if r[0] == 'OK')} OK")
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["dossier", "concepts", "histoire"])
    ap.add_argument("cible", nargs="?")
    ap.add_argument("--muet", action="store_true", help="n'imprime pas le rendu Markdown")
    a = ap.parse_args()
    b = Base()
    if a.action == "dossier":
        dossier(b)
        return
    if not a.cible:
        raise SystemExit("cible manquante (fichier de concepts ou id de projet)")
    res, md = concepts(b, a.cible) if a.action == "concepts" else histoire(b, a.cible)
    if not a.muet:
        print(md)
    raise SystemExit(1 if imprimer(res) else 0)


if __name__ == "__main__":
    main()
