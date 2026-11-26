"""Analyse des vidéos virales.

Usage :
    python outils/analyse.py                 # traite tous les liens de sources/liens.txt pas encore analysés
    python outils/analyse.py URL [URL ...]   # traite ces liens

Un lien de vidéo (…/video/123) = cette vidéo.
Un lien de compte (…/@nom) = ses 5 vidéos les plus vues (option --top N).
    python outils/analyse.py --releve-comptes   # relève les vues récentes des comptes déjà analysés

Pour chaque vidéo, crée analyses/<id>/ :
    meta.json        vues, likes, commentaires, partages, durée, description
    transcript.json  texte mot par mot avec temps
    plans.json       temps de chaque coupe, durée moyenne des plans
    planche.jpg      une image par plan, numérotée, avec son temps
    brut.json        tout réuni pour la fiche d'analyse
Et analyses/_comptes/<compte>.json : vues des 60 dernières vidéos du compte (performance relative).
Ensuite : Claude écrit fiche.md + mecaniques.json, puis `python3 outils/mecaniques.py` (voir /analyser).
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import ANALYSES, SOURCES, duree, ecrire_json, police, run, whisper, a_un_son  # noqa: E402

VIDEOS = SOURCES / "videos"
COMPTES = ANALYSES / "_comptes"
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


def releve_compte(url):
    """Vues des 60 dernières vidéos d'un compte -> analyses/_comptes/<compte>.json (référence de performance relative).
    Sans ce relevé, mecaniques.py compare seulement aux vidéos analysées du compte (top vues : biaisé)."""
    out = run(YTDLP + ["--flat-playlist", "-J", "--playlist-end", "60", url])
    data = json.loads(out[out.index("{"):])
    entrees = [e for e in data.get("entries", []) if e]
    vues = sorted(e["view_count"] for e in entrees if e.get("view_count") is not None)
    compte = (data.get("uploader") or data.get("channel") or url.rstrip("/").split("@")[-1]).lstrip("@")
    if vues:
        COMPTES.mkdir(parents=True, exist_ok=True)
        ecrire_json(COMPTES / f"{compte}.json", {
            "compte": compte, "date": date.today().isoformat(), "n": len(vues),
            "mediane_vues": vues[len(vues) // 2] if len(vues) % 2 else (vues[len(vues) // 2 - 1] + vues[len(vues) // 2]) / 2,
            "abonnes": data.get("channel_follower_count"),
            "videos": [{"id": e.get("id"), "vues": e.get("view_count")} for e in entrees],
        })
    return entrees


def depuis_compte(url, top):
    """Renvoie les URLs des vidéos les plus vues d'un compte (et enregistre son relevé de vues)."""
    entrees = releve_compte(url)
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


def coupes_en_fondu(mp4, seuil=15, ecart=15):
    """Compare chaque image à celle d'il y a 0,5 s : un pic = un fondu enchaîné entre deux plans."""
    import numpy as np
    w, h = 36, 64
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf", f"scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    fps = 30.0
    out = run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(mp4)])
    a_, _, b_ = out.strip().splitlines()[0].partition("/")
    fps = float(a_) / float(b_ or 1)
    a = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float)
    d = np.zeros(len(a))
    d[ecart:] = np.abs(a[ecart:] - a[:-ecart]).mean(axis=(1, 2))
    coupes, der = [], -10 ** 9
    for i in range(1, len(d) - 1):
        if d[i] >= seuil and d[i] == d[max(0, i - ecart):i + ecart + 1].max() and i - der > fps:
            coupes.append(round((i - ecart / 2) / fps, 2))
            der = i
    return coupes


def detecter_plans(mp4, total):
    out = run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-vf",
               "select='gt(scene,0.28)',showinfo", "-an", "-f", "null", "-"])
    coupes = [float(t) for t in re.findall(r"pts_time:([\d.]+)", out)]
    coupes = [c for i, c in enumerate(coupes) if c > 0.3 and (i == 0 or c - coupes[i - 1] > 0.4)]
    if len(coupes) < total / 12:  # montage en fondus (0,3-0,8 s) : invisible pour le filtre scene
        coupes = coupes_en_fondu(mp4)
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
        "favoris": info.get("save_count"),  # absent selon la version de yt-dlp : reste null, jamais estimé
        "abonnes": info.get("channel_follower_count"),
        "date": info.get("upload_date"), "duree": round(total, 1),
        "musique": info.get("track") or info.get("artist"),
    }
    if meta["vues"]:
        for k in ("likes", "commentaires", "partages", "favoris"):  # donnée absente = pas de taux
            if meta[k] is not None:
                meta[f"taux_{k}"] = round(meta[k] / meta["vues"] * 100, 2 if k == "likes" else 3)
    ecrire_json(dos / "meta.json", meta)
    if meta["compte"] and not (COMPTES / f"{meta['compte']}.json").exists():
        try:  # référence de performance relative ; facultatif
            releve_compte(f"https://www.tiktok.com/@{meta['compte']}")
        except (SystemExit, ValueError):
            print(f"   (relevé du compte {meta['compte']} impossible : performance relative sur le corpus seulement)")

    if a_un_son(mp4):
        wav = dos / "_audio.wav"
        run(["ffmpeg", "-hide_banner", "-y", "-i", str(mp4), "-ac", "1", "-ar", "16000", str(wav)])
        try:
            tr = whisper(wav)
        except ImportError:  # cloud sans faster-whisper : découpage et planches quand même
            print("   (faster-whisper absent : transcription à faire depuis les sous-titres incrustés)")
            tr = {"langue": None, "phrases": [], "mots": [], "manquante": True}
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
    ap.add_argument("--releve-comptes", action="store_true",
                    help="relève les vues récentes de chaque compte déjà analysé (référence de performance relative)")
    args = ap.parse_args()
    if args.releve_comptes:
        comptes = sorted({json.loads(f.read_text(encoding="utf-8")).get("compte") for f in ANALYSES.glob("*/meta.json")} - {None})
        for c in comptes:
            try:
                n = len(releve_compte(f"https://www.tiktok.com/@{c}"))
                print(f"compte {c} : {n} vidéos relevées")
            except (SystemExit, ValueError):
                print(f"compte {c} : relevé impossible")
        return
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
