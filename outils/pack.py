"""Assemble les prompts d'un épisode depuis la bible et produit :
    projets/<projet>/episodes/epNNN/pack.json   prompts prêts (lu par monter.py)
    projets/<projet>/episodes/epNNN/pack.html   page locale avec boutons Copier
et met à jour projets/<projet>/episodes/historique.json.

Usage : python outils/pack.py <projet> [epNNN]   (ep001 par défaut ; refuse si verifier.py échoue, sauf --forcer)
"""
import html
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bible import Bible, ouverture_chatgpt, prompt_grok, prompt_image, prompt_portrait  # noqa: E402
from commun import args_projet, compat_plan, dialogues, duree_plan, ecrire_json, lire_json  # noqa: E402


def construire(b, nom):
    ep = lire_json(b.episodes / nom / "episode.json")
    ouverture, refs = ouverture_chatgpt(b, ep)
    plans = []
    for p in ep["plans"]:
        plans.append({
            "n": p["n"], "duree": duree_plan(p), "role": p.get("role", ""),
            "titre": f"{b.lieux[p['lieu']]['nom']} · {p['cadrage']}",
            "dialogues": [{"t": d["t"], "qui": b.nom(d["parle"]), "texte": d["texte"]} for d in dialogues(p)],
            "replique": compat_plan(p)["replique"], "parle": compat_plan(p)["parle"],
            "texte_ecran": p.get("texte_ecran", ""),
            "image": prompt_image(b, p),
            "image_fin": prompt_image(b, p, fin=True) if p.get("fin") else "",
            "grok": prompt_grok(b, p),
        })
    pack = {
        "id": nom, "numero": ep["numero"], "titre": ep["titre"], "resume": ep.get("resume", ""),
        "projet": b.id, "projet_titre": b.projet.get("titre", b.id), "type": b.projet.get("type", "unique"),
        "portraits": [{"id": pid, "nom": b.nom(pid), "ref": b.persos[pid].get("ref", f"refs/{pid}.png"),
                       "prompt": prompt_portrait(b, pid)}
                      for pid in b.ordre if any(pid == x["id"] for p in ep["plans"] for x in p["persos"])],
        "ouverture": ouverture, "refs": refs, "plans": plans,
        "titre_couverture": ep.get("titre_couverture", ""),
        "publication": (ep.get("legende", "") + "\n\n" + " ".join(ep.get("hashtags", []))).strip(),
        "commentaire": ep.get("commentaire_epingle", ""),
        "texte_accroche": ep.get("texte_accroche", ""),
        "hooks_alternatifs": ep.get("hooks_alternatifs", []),
        "question_milieu": ep.get("question_milieu", {}),
        "duree_totale": sum(x["duree"] for x in plans),
    }
    ecrire_json(b.episodes / nom / "pack.json", pack)
    return ep, pack


def maj_historique(b, ep):
    f = b.episodes / "historique.json"
    hist = lire_json(f) if f.exists() else []
    hist = [h for h in hist if h["numero"] != ep["numero"]]
    lieux = [p["lieu"] for p in ep["plans"]]
    hist.append({
        "numero": ep["numero"], "titre": ep["titre"], "format": ep.get("format"),
        "accroche_type": ep.get("accroche_type"), "cliff_type": ep.get("cliff_type"),
        "centre": ep.get("centre"), "lieu_principal": Counter(lieux).most_common(1)[0][0],
        "lieux": sorted(set(lieux)), "fils_avances": ep.get("fils_avances", []), "revele": ep.get("revele", []),
        "temps_parole": dict(Counter(d["parle"] for p in ep["plans"] for d in dialogues(p))),
        "repliques": [d["texte"] for p in ep["plans"] for d in dialogues(p)],
        "resume": ep.get("resume"), "fin": ep.get("fin"),
    })
    ecrire_json(f, sorted(hist, key=lambda h: h["numero"]))


def esc(s):
    return html.escape(str(s or ""))


CSS = """
:root{--bg:#f4f2ec;--card:#fff;--ink:#17171b;--mute:#6b6b73;--line:#e2ddd2;--acc:#d9572b;--ok:#2f8f4e;--box:#faf8f3;--gpt:#10a37f;--grok:#17171b}
@media(prefers-color-scheme:dark){:root{--bg:#111113;--card:#1b1b1f;--ink:#f1f0ec;--mute:#9a9aa3;--line:#2c2c32;--box:#141417;--grok:#f1f0ec}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:860px;margin:auto;padding:20px 16px 80px}h1{font-size:22px;margin:0 0 6px}h2{font-size:16px;margin:26px 0 10px}
.res{color:var(--mute);margin:0 0 10px}.cast{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 6px}.cast span{background:var(--card);border:1px solid var(--line);border-radius:99px;padding:3px 10px;font-size:13px}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);padding:10px 0;margin-bottom:6px}.bar div{height:8px;background:var(--line);border-radius:9px;overflow:hidden}.bar i{display:block;height:100%;width:0;background:var(--ok);transition:width .3s}
.bar p{margin:4px 0 0;font-size:13px;color:var(--mute)}
section{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin:0 0 12px}
h3{margin:0 0 4px;font-size:15px}h3 b{color:var(--acc);margin-right:6px}.r{color:var(--mute);margin:0 0 10px;font-size:14px}.r q{color:var(--ink);font-style:italic}
.g{display:grid;grid-template-columns:1fr 1fr;gap:10px}.g3{grid-template-columns:1fr 1fr 1fr}@media(max-width:820px){.g3{grid-template-columns:1fr}}@media(max-width:640px){.g{grid-template-columns:1fr}}
.dl{margin:0 0 10px;padding:0;list-style:none;font-size:14px}.dl li{padding:2px 0}.dl code{color:var(--acc);font-weight:700;margin-right:6px}
.d{font-size:11px;font-weight:800;padding:2px 7px;border-radius:6px;background:var(--line);margin-left:6px}.d.x{background:#7c3aed;color:#fff}
.tl{display:flex;gap:2px;margin:8px 0 2px}.tl span{height:26px;border-radius:4px;background:var(--line);font-size:11px;display:flex;align-items:center;justify-content:center;font-weight:700}.tl span.x{background:#7c3aed;color:#fff}.tl span.k{background:var(--acc);color:#fff}
.ck{list-style:none;padding:0;margin:0}.ck li{padding:5px 0;border-bottom:1px solid var(--line)}.ck label{cursor:pointer}
.p{border:1px solid var(--line);border-radius:10px;background:var(--box);display:flex;flex-direction:column}
.p header{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 10px;border-bottom:1px solid var(--line);font-weight:700;font-size:13px}
.tag{font-size:11px;font-weight:800;padding:2px 7px;border-radius:6px;color:#fff;background:var(--gpt)}.tag.k{background:var(--grok);color:var(--bg)}.tag.o{background:var(--acc)}
pre{margin:0;padding:10px;white-space:pre-wrap;word-break:break-word;font:13px/1.45 ui-monospace,Consolas,monospace;max-height:220px;overflow:auto;flex:1;user-select:all;-webkit-user-select:all}
button.c{border:0;border-radius:8px;padding:8px 14px;font:700 13px system-ui;background:var(--acc);color:#fff;cursor:pointer;white-space:nowrap}
button.c.u{background:var(--ok)}button.c.w{background:#b7791f}
"""

JS = r"""
const K='pack:'+location.pathname;let fait={};try{fait=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
const bs=[...document.querySelectorAll('button.c')];
function maj(){const n=bs.filter(b=>fait[b.dataset.k]).length;document.querySelector('.bar i').style.width=(100*n/bs.length)+'%';
document.querySelector('.bar p').textContent=n+' / '+bs.length+' prompts copiés';bs.forEach(b=>{if(fait[b.dataset.k]&&!b.classList.contains('w')){b.classList.add('u');b.textContent='Copié ✓'}})}
function secours(t){const a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.focus();a.select();let ok=false;try{ok=document.execCommand('copy')}catch(e){}a.remove();return ok}
bs.forEach(b=>b.onclick=async()=>{const pre=document.getElementById(b.dataset.k);const t=pre.textContent;let ok=false;
try{await navigator.clipboard.writeText(t);ok=true}catch(e){ok=secours(t)}
if(ok){fait[b.dataset.k]=1;try{localStorage.setItem(K,JSON.stringify(fait))}catch(e){}b.classList.remove('w');maj()}
else{const r=document.createRange();r.selectNodeContents(pre);const s=getSelection();s.removeAllRanges();s.addRange(r);b.classList.add('w');b.textContent='Texte sélectionné → Ctrl+C'}});
document.getElementById('raz').onclick=()=>{fait={};try{localStorage.removeItem(K)}catch(e){}bs.forEach(b=>{b.classList.remove('u','w');b.textContent='Copier'});maj()};
maj();
"""


CHECKLIST = [
    "Durée finale entre 61 et 75 s (éligible Récompenses Créateurs), aucun silence de plus de 0,5 s",
    "Texte d'accroche à l'écran dès la 1re image (0 à 2 s), gros, centré haut",
    "Sous-titres mot par mot en couleur par personnage (fait par /monter)",
    "Dernière image qui s'enchaîne avec la première (boucle = revisionnages)",
    "Couverture = image la plus choquante + titre de couverture (5 mots max)",
    "Musique tendue TikTok en fond à 10-15 % (son tendance de la semaine si possible)",
    "Activer « Contenu généré par IA » dans les paramètres de publication (protège la portée)",
    "Poster entre 18 h et 21 h, puis répondre aux 20 premiers commentaires dans l'heure",
    "Épingler le commentaire de vote juste après la publication",
    "Série : poster la partie 2 quand la partie 1 dépasse 100 000 vues, avec la même réplique de fin en ouverture",
]


def page_locale(b, nom, pack):
    compteur = iter(range(1, 999))

    def bloc(label, texte, tag="ChatGPT", cls=""):
        k = f"p{next(compteur)}"
        return (f'<div class="p"><header><span><span class="tag {cls}">{esc(tag)}</span> {esc(label)}</span>'
                f'<button class="c" data-k="{k}">Copier</button></header><pre id="{k}">{esc(texte)}</pre></div>')

    cast = "".join(f"<span><b>{esc(x['nom'])}</b> · {esc(x['animal'])}</span>"
                   for x in (b.persos[pid] for pid in b.ordre))
    portraits = "".join(bloc(f"{x['nom']} → enregistrer {x['ref']}", x['prompt']) for x in pack["portraits"])
    tl = "".join(f'<span class="{"x" if p["duree"] >= 10 else ""}{" k" if p["role"] in ("accroche", "retournement", "cliff") else ""}" '
                 f'style="flex:{p["duree"]}" title="Plan {p["n"]} · {p["duree"]} s · {esc(p["role"])}">{p["n"]}</span>'
                 for p in pack["plans"])

    def carte(p):
        dl = "".join(f"<li><code>{esc(d['t'])}s</code><b>{esc(d['qui'])}</b> : « {esc(d['texte'])} »</li>"
                     for d in p["dialogues"]) or "<li>Plan muet (réactions + bruitages)</li>"
        blocs = [bloc(f"Image {p['n']} · début", p['image'])]
        if p["image_fin"]:
            blocs.append(bloc(f"Image {p['n']} · fin", p['image_fin']))
        blocs.append(bloc(f"Vidéo {p['n']} · {p['duree']} s (joindre l'image {p['n']}{' début + fin' if p['image_fin'] else ''})",
                          p['grok'], 'Grok', 'k'))
        ecran = ("<p class=\"r\">Texte à l'écran au montage : <b>" + esc(p["texte_ecran"]) + "</b></p>") if p["texte_ecran"] else ""
        return (f'<section><h3><b>{p["n"]:02d}</b>{esc(p["titre"])}<span class="d{" x" if p["duree"] >= 10 else ""}">{p["duree"]} s</span>'
                f'{"<span class=d>" + esc(p["role"]) + "</span>" if p["role"] in ("accroche", "retournement", "cliff") else ""}</h3>'
                f'<ul class="dl">{dl}</ul>{ecran}<div class="g{" g3" if len(blocs) == 3 else ""}">{"".join(blocs)}</div></section>')

    cartes = "".join(carte(p) for p in pack["plans"])
    hooks = ""
    if pack.get("hooks_alternatifs"):
        hooks = ("<h2>Hooks de rechange <small>(si la vidéo plafonne sous 2 000 vues en 2 h, refais SEULEMENT le plan 1 avec un de ceux-là et reposte)</small></h2><section><ul class=dl>"
                 + "".join(f"<li><code>{chr(65 + i)}</code>{esc(h)}</li>" for i, h in enumerate(pack["hooks_alternatifs"]))
                 + "</ul></section>")
    checklist = "".join(f'<li><label><input type="checkbox"> {x}</label></li>' for x in CHECKLIST)
    ep = f" · épisode {pack['numero']}" if pack['type'] == 'serie' else ''
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(pack['projet_titre'])}{ep}</title><style>{CSS}</style></head><body><main>
<h1>{esc(pack['projet_titre'])}{ep} · {esc(pack['titre'])}</h1><p class="res">{esc(pack['resume'])}</p><div class="cast">{cast}</div>
<div class="tl">{tl}</div><p class="r">{len(pack['plans'])} plans · {pack['duree_totale']} s de rush (≈ {round(pack['duree_totale'] * 0.85)} s après montage serré) · <span style="color:#7c3aed">violet = 10 s</span> · <span style="color:var(--acc)">orange = moment clé</span></p>
<div class="bar"><div><i></i></div><p></p></div>
<h2>Étape 0 · Portraits de référence <small>(ChatGPT, une fois par personnage)</small></h2>
<section><p class="r">Un prompt = une image. Enregistre chaque portrait sous le nom indiqué : il sert à garder les mêmes visages partout.</p><div class="g">{portraits}</div></section>
<h2>Étape 1 · Ouverture <small>(nouvelle conversation ChatGPT)</small></h2>
<section><p class="r">Joins d'abord les portraits : {esc(', '.join(pack['refs']))}. Puis colle ce message.</p>{bloc("Message d'ouverture", pack['ouverture'], 'ChatGPT', 'o')}</section>
<h2>Étape 2 · Les {len(pack['plans'])} plans <small>(Image → ChatGPT, puis dans Grok : image + prompt vidéo, en réglant la durée indiquée)</small></h2>
{cartes}
{hooks}
<h2>Étape 3 · Publication</h2>
<section><div class="g">{bloc("Légende + hashtags", pack['publication'], 'TikTok', 'o')}{bloc("Commentaire épinglé", pack['commentaire'], 'TikTok', 'o')}</div></section>
<h2>Check-list avant de poster</h2><section><ul class="ck">{checklist}</ul></section>
<p style="text-align:center"><button class="c" id="raz" style="background:var(--mute)">Remettre la progression à zéro</button></p>
</main><script>{JS}</script></body></html>"""
    (b.episodes / nom / "pack.html").write_text(page, encoding="utf-8")


def main():
    projet, nom = args_projet(sys.argv[1:])
    if "--forcer" not in sys.argv:
        r = subprocess.run([sys.executable, str(Path(__file__).parent / "verifier.py"), projet, nom])
        if r.returncode:
            raise SystemExit("Pack refusé : corrige les ÉCHECS ci-dessus (ou --forcer).")
    b = Bible(projet)
    ep, pack = construire(b, nom)
    if b.serie:
        maj_historique(b, ep)
    page_locale(b, nom, pack)
    print(f"OK : {(b.episodes / nom / 'pack.html').as_posix()} ({len(pack['plans'])} plans)")


if __name__ == "__main__":
    main()
