"""Analyse des vidéos virales.

Usage :
    python outils/analyse.py                 # traite tous les liens de sources/liens.txt pas encore analysés
    python outils/analyse.py URL [URL ...]   # traite ces liens

Un lien de vidéo (…/video/123) = cette vidéo.
Un lien de compte (…/@nom) = ses 5 vidéos les plus vues (option --top N).

Pour chaque vidéo, crée analyses/<id>/ :
    meta.json        vues, likes, commentaires, partages, durée, description
    transcript.json  texte mot par mot avec temps
    plans.json       temps de chaque coupe, durée moyenne des plans
    planche.jpg      une image par plan, numérotée, avec son temps
    brut.json        tout réuni pour la fiche d'analyse
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import ANALYSES, SOURCES, duree, ecrire_json, police, run, whisper, a_un_son  # noqa: E402

VIDEOS = SOURCES / "videos"
YTDLP = [sys.executable, "-m", "yt_dlp", "--no-warnings", "--quiet"]


def lister_liens(args):
    if args.urls:
        return args.urls
    f = SOURCES / "liens.txt"
    if not f.exists():
        print("Aucun lien. Colle des liens TikTok dans", f)
        return []
    return [l.strip() for l in f.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")]


def depuis_compte(url, top):
    """Renvoie les URLs des vidéos les plus vues d'un compte."""
    out = run(YTDLP + ["--flat-playlist", "-J", "--playlist-end", "60", url])
    data = json.loads(out[out.index("{"):])
    entrees = [e for e in data.get("entries", []) if e]
    entrees.sort(key=lambda e: e.get("view_count") or 0, reverse=True)
    return [e.get("url") or e.get("webpage_url") for e in entrees[:top]]


def id_de(url):
    m = re.search(r"/video/(\d+)", url)
    return m.group(1) if m else None


def telecharger(url):
    vid = id_de(url) or run(YTDLP + ["--print", "id", url]).strip().splitlines()[-1]
    dossier = VIDEOS / vid
    dossier.mkdir(parents=True, exist_ok=True)
    mp4 = next(dossier.glob("*.mp4"), None)
    if mp4 is None:
        run(YTDLP + ["-f", "mp4/best", "--write-info-json", "-o", str(dossier / "%(id)s.%(ext)s"), url])
        mp4 = next(dossier.glob("*.mp4"))
    info = next(dossier.glob("*.info.json"), None)
    return mp4, (json.loads(info.read_text(encoding="utf-8")) if info else {})


def detecter_plans(mp4, total):
    out = run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-vf",
               "select='gt(scene,0.28)',showinfo", "-an", "-f", "null", "-"])
    coupes = [float(t) for t in re.findall(r"pts_time:([\d.]+)", out)]
    coupes = [c for i, c in enumerate(coupes) if c > 0.3 and (i == 0 or c - coupes[i - 1] > 0.4)]
    bornes = [0.0] + coupes + [total]
    plans = [{"n": i + 1, "debut": round(a, 2), "fin": round(b, 2), "duree": round(b - a, 2)}
             for i, (a, b) in enumerate(zip(bornes, bornes[1:])) if b - a > 0.2]
    return plans


def planche(mp4, plans, sortie):
    from PIL import Image, ImageDraw
    tmp = sortie.parent / "_frames"
    tmp.mkdir(exist_ok=True)
    choisis = plans if len(plans) <= 30 else plans[:: max(1, len(plans) // 30)][:30]
    vignettes = []
    for p in choisis:
        t = (p["debut"] + p["fin"]) / 2
        f = tmp / f"{p['n']:03d}.jpg"
        run(["ffmpeg", "-hide_banner", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1",
             "-vf", "scale=270:-2", str(f)])
        vignettes.append((p, Image.open(f).convert("RGB")))
    if not vignettes:
        return
    w, h = vignettes[0][1].size
    cols = 6
    rows = (len(vignettes) + cols - 1) // cols
    img = Image.new("RGB", (cols * w, rows * (h + 34)), "white")
    d = ImageDraw.Draw(img)
    font = police(20)
    for i, (p, v) in enumerate(vignettes):
        x, y = (i % cols) * w, (i // cols) * (h + 34)
        img.paste(v.resize((w, h)), (x, y + 34))
        d.text((x + 6, y + 6), f"#{p['n']}  {p['debut']:.1f}s ({p['duree']:.1f}s)", fill="black", font=font)
    img.save(sortie, quality=85)
    for f in tmp.glob("*.jpg"):
        f.unlink()
    tmp.rmdir()


def analyser(url):
    local = Path(url)
    vid = local.stem if local.exists() else id_de(url)
    if vid and (ANALYSES / vid / "brut.json").exists():
        print(f"déjà analysée : {vid}")
        return
    print(f"→ {url}")
    mp4, info = (local, {}) if local.exists() else telecharger(url)
    vid = vid or info.get("id") or mp4.stem
    dos = ANALYSES / vid
    dos.mkdir(parents=True, exist_ok=True)
    total = duree(mp4)

    meta = {
        "id": vid, "url": url, "compte": info.get("uploader") or info.get("channel"),
        "description": info.get("description") or info.get("title"),
        "vues": info.get("view_count"), "likes": info.get("like_count"),
        "commentaires": info.get("comment_count"), "partages": info.get("repost_count"),
        "date": info.get("upload_date"), "duree": round(total, 1),
        "musique": info.get("track") or info.get("artist"),
    }
    if meta["vues"]:
        meta["taux_likes"] = round((meta["likes"] or 0) / meta["vues"] * 100, 2)
        meta["taux_commentaires"] = round((meta["commentaires"] or 0) / meta["vues"] * 100, 3)
    ecrire_json(dos / "meta.json", meta)

    if a_un_son(mp4):
        wav = dos / "_audio.wav"
        run(["ffmpeg", "-hide_banner", "-y", "-i", str(mp4), "-ac", "1", "-ar", "16000", str(wav)])
        tr = whisper(wav)
        wav.unlink()
    else:
        tr = {"langue": None, "phrases": [], "mots": []}
    ecrire_json(dos / "transcript.json", tr)

    plans = detecter_plans(mp4, total)
    moy = round(sum(p["duree"] for p in plans) / len(plans), 2) if plans else None
    ecrire_json(dos / "plans.json", {"nombre": len(plans), "duree_moyenne": moy, "plans": plans})
    planche(mp4, plans, dos / "planche.jpg")

    texte = " ".join(p["texte"] for p in tr["phrases"])
    mots = tr["mots"]
    brut = {
        "meta": meta,
        "langue": tr["langue"],
        "texte_complet": texte,
        "accroche_3s": " ".join(m["mot"] for m in mots if m["debut"] < 3.0),
        "fin_5s": " ".join(m["mot"] for m in mots if m["debut"] > total - 5),
        "mots_par_seconde": round(len(mots) / total, 2) if total else None,
        "premier_mot_a": mots[0]["debut"] if mots else None,
        "nombre_plans": len(plans),
        "duree_moyenne_plan": moy,
        "phrases": tr["phrases"],
        "plans": plans,
    }
    ecrire_json(dos / "brut.json", brut)
    print(f"   ok : {meta['vues']} vues, {total:.0f} s, {len(plans)} plans, {len(mots)} mots -> {dos}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--top", type=int, default=5, help="vidéos par compte")
    args = ap.parse_args()
    liens = []
    for u in lister_liens(args):
        if "/video/" in u or "vm.tiktok" in u or "vt.tiktok" in u:
            liens.append(u)
        elif "@" in u:
            print(f"compte : {u} (top {args.top})")
            liens += depuis_compte(u, args.top)
        else:
            liens.append(u)
    for u in liens:
        try:
            analyser(u)
        except SystemExit:
            print(f"   échec : {u} (lien privé, supprimé ou bloqué)")


if __name__ == "__main__":
    main()
