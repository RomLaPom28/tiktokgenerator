"""Découpe une vidéo virale pour la copier (commande /copier).

Usage :
    python outils/copier.py <lien TikTok | id déjà analysé | fichier.mp4> [lien2 lien3 …]
    (plusieurs liens = une série source : partie 1, partie 2…, dans l'ordre)

1. Si la vidéo n'est pas encore analysée : téléchargement + transcription + détection des plans
   (analyse.py : PC uniquement, il faut yt-dlp, ffmpeg et faster-whisper).
2. Produit dans analyses/<id>/ :
    decoupage.json   chaque plan avec ses répliques (numérotées r1, r2… = ordre du transcript)
    decoupage.md     la même chose lisible : c'est ce que Claude lit pour écrire la dissection
    planches/        planches de 12 plans (grande taille) pour voir personnages et décors
                     (seulement si la vidéo est sur ce poste ; sinon planche.jpg de l'analyse)
Ensuite Claude écrit dissection.json + dissection.md (voir .claude/skills/copier/SKILL.md).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import ANALYSES, SOURCES, ecrire_json, lire_json, police, run  # noqa: E402


def identifier(arg):
    local = Path(arg)
    if local.suffix.lower() in (".mp4", ".mov", ".webm") and local.exists():
        return local.stem, local
    if re.fullmatch(r"\d{8,}", arg):
        return arg, None
    m = re.search(r"/video/(\d+)", arg)
    return (m.group(1) if m else None), None


def trouver_mp4(vid, local):
    if local:
        return local
    return next((SOURCES / "videos" / vid).glob("*.mp4"), None) if (SOURCES / "videos" / vid).exists() else None


def decouper(brut):
    """Range chaque phrase du transcript dans le plan qui contient son milieu."""
    plans = [dict(p, repliques=[]) for p in brut["plans"]] or [{"n": 1, "debut": 0, "fin": 9e9, "duree": 0, "repliques": []}]
    for i, ph in enumerate(brut["phrases"], 1):
        mil = (ph["debut"] + ph["fin"]) / 2
        cible = next((p for p in plans if p["debut"] <= mil < p["fin"]), plans[-1])
        cible["repliques"].append({"r": f"r{i}", "t": f"{ph['debut']:.1f}-{ph['fin']:.1f}", "texte": ph["texte"]})
    return plans


def ecrire_md(vid, brut, plans, sortie):
    m = brut["meta"]
    vues = f"{m['vues'] / 1e6:.1f} M vues" if m.get("vues") else "vues ?"
    lignes = [f"# Découpage {vid} · {m.get('compte') or ''}",
              f"{m.get('description') or ''}", "",
              f"{vues} · likes {m.get('taux_likes', '?')} % · commentaires {m.get('taux_commentaires', '?')} % · "
              f"{m.get('duree')} s · {len(plans)} plans · plan moyen {brut.get('duree_moyenne_plan')} s · "
              f"{brut.get('mots_par_seconde')} mots/s · 1er mot à {brut.get('premier_mot_a')} s", "",
              "Répliques numérotées r1, r2… : ces numéros servent de référence (`source`) dans l'adaptation.", ""]
    for p in plans:
        lignes.append(f"## Plan {p['n']} · {p['debut']:.1f}-{p['fin']:.1f} s ({p['duree']:.1f} s)")
        lignes += [f"- **{r['r']}** `{r['t']}` {r['texte']}" for r in p["repliques"]] or ["- (sans parole)"]
        lignes.append("")
    sortie.write_text("\n".join(lignes), encoding="utf-8")


def planches(mp4, plans, dossier):
    from PIL import Image, ImageDraw
    dossier.mkdir(exist_ok=True)
    for f in dossier.glob("*.jpg"):
        f.unlink()
    w, h, cols, rows = 300, 540, 4, 3
    titre, legende = police(22), police(15, gras=False)
    for k in range(0, len(plans), cols * rows):
        lot = plans[k:k + cols * rows]
        img = Image.new("RGB", (cols * w, rows * (h + 70)), "white")
        d = ImageDraw.Draw(img)
        for i, p in enumerate(lot):
            t = (p["debut"] + p["fin"]) / 2
            tmp = dossier / "_f.jpg"
            run(["ffmpeg", "-hide_banner", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1",
                 "-vf", f"scale={w}:{h - 8}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2", str(tmp)])
            x, y = (i % cols) * w, (i // cols) * (h + 70)
            img.paste(Image.open(tmp).convert("RGB"), (x, y + 28))
            d.text((x + 6, y + 3), f"#{p['n']}  {p['debut']:.1f}s ({p['duree']:.1f}s)", fill="black", font=titre)
            parole = " ".join(r["texte"] for r in p["repliques"])[:70]
            d.text((x + 6, y + h + 32), parole, fill="#444", font=legende)
            tmp.unlink()
        img.save(dossier / f"planche_{k // (cols * rows) + 1:02d}.jpg", quality=82)


def sous_titres(mp4, dossier, fps=10, haut=0.69, bas=0.81):
    """Vidéo sans transcription (pas de whisper) mais sous-titres incrustés : une case par mot affiché,
    avec son temps, pour que Claude les lise et écrive transcript.json à la main."""
    import subprocess
    import numpy as np
    from PIL import Image, ImageDraw
    W, H = (int(x) for x in run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                 "stream=width,height", "-of", "csv=p=0", str(mp4)]).strip().split(",")[:2])
    y0, y1 = int(H * haut), int(H * bas)
    w, h = 288, max(10, (y1 - y0) // 2)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf",
                          f"fps={fps},crop={W}:{y1 - y0}:0:{y0},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    img = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    blanc = (img.min(axis=3) > 215)
    cases, prec = [], None
    for i, m in enumerate(blanc):
        if m.sum() < 15:
            prec = None
            continue
        if prec is None or (m ^ prec).sum() > 0.35 * max(m.sum(), prec.sum()):
            cases.append((i / fps, Image.fromarray(img[i])))
        prec = m
    for f in dossier.glob("soustitres_*.jpg"):
        f.unlink()
    cols, rows = 5, 20
    titre = police(14)
    for k in range(0, len(cases), cols * rows):
        lot = cases[k:k + cols * rows]
        page = Image.new("RGB", (cols * w, ((len(lot) + cols - 1) // cols) * (h + 18)), "white")
        d = ImageDraw.Draw(page)
        for j, (t, c) in enumerate(lot):
            x, y = (j % cols) * w, (j // cols) * (h + 18)
            d.text((x + 4, y + 1), f"{t:.1f}s", fill="red", font=titre)
            page.paste(c, (x, y + 18))
        page.save(dossier / f"soustitres_{k // (cols * rows) + 1:02d}.jpg", quality=85)
    return len(cases)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:  # plusieurs liens = une série source, dans l'ordre des épisodes
        traiter(arg)


def traiter(arg):
    vid, local = identifier(arg)
    if not vid or not (ANALYSES / vid / "brut.json").exists():
        from analyse import analyser
        analyser(str(local or arg))
        if not vid:  # lien court vm.tiktok : retrouver l'id dans sources/videos
            vid = max((SOURCES / "videos").iterdir(), key=lambda p: p.stat().st_mtime).name
    dos = ANALYSES / vid
    if not (dos / "brut.json").exists():
        raise SystemExit(f"Analyse introuvable pour {arg}")
    brut = lire_json(dos / "brut.json")
    plans = decouper(brut)
    ecrire_json(dos / "decoupage.json", {"id": vid, "meta": brut["meta"], "plans": plans})
    ecrire_md(vid, brut, plans, dos / "decoupage.md")
    mp4 = trouver_mp4(vid, local)
    if mp4:
        planches(mp4, plans, dos / "planches")
        vues = f"{dos / 'planches'} ({len(list((dos / 'planches').glob('*.jpg')))} planches)"
    else:
        vues = f"{dos / 'planche.jpg'} (vidéo absente de ce poste : planche réduite de l'analyse)"
    if mp4 and not brut["phrases"]:
        n = sous_titres(mp4, dos)
        print(f"  pas de transcription : {n} mots incrustés à lire dans {dos}/soustitres_*.jpg "
              "-> écrire transcript.json (phrases) puis relancer copier.py")
    nb = sum(len(p["repliques"]) for p in plans)
    print(f"OK {vid} : {len(plans)} plans, {nb} répliques\n  texte : {dos / 'decoupage.md'}\n  images : {vues}")


if __name__ == "__main__":
    main()
