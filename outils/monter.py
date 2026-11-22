"""Montage automatique d'un épisode.

Usage :
    python outils/monter.py ep001              # prend clips/ ou, s'il est vide, les N dernières vidéos de Téléchargements
    python outils/monter.py ep001 --refaire    # reprend les clips depuis Téléchargements même si clips/ est rempli

Produit dans episodes/ep001/ :
    ep001_final.mp4   1080x1920, 30 i/s, sous-titres incrustés, -14 LUFS
    couverture.jpg    image de couverture avec le titre
    publication.txt   légende, hashtags, commentaire à épingler
    rapport.md        contrôles mesurés
"""
import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bible import Bible  # noqa: E402
from commun import FONT_BOLD, MUSIQUE, a_un_son, compat_plan, duree, lire_json, run, whisper  # noqa: E402

DUREE_MIN = 61.0  # au-dessus d'1 minute pour la rémunération TikTok


# ---------- 1b. rythme : couper les silences de début et de fin de chaque clip Grok ----------
def rythme(clips, plans, dos):
    """Renvoie pour chaque clip la fenêtre [début, fin] à garder."""
    fen = []
    for i, c in enumerate(clips):
        d = duree(c)
        plan = plans[i] if i < len(plans) else {}
        if plan.get("garder"):
            fen.append((float(plan["garder"][0]), float(plan["garder"][1]), d))
            continue
        mots = []
        if a_un_son(c) and plan.get("replique"):
            wav = dos / "_r.wav"
            run(["ffmpeg", "-hide_banner", "-y", "-i", str(c), "-ac", "1", "-ar", "16000", str(wav)])
            mots = whisper(wav, langue="fr", prompt=plan["replique"])["mots"]
            wav.unlink()
        if mots:
            a = max(0.0, mots[0]["debut"] - 0.30)
            b = min(d, mots[-1]["fin"] + 0.60)
            if i == 0:
                a = 0.0  # l'accroche démarre sur la première image
        else:
            a, b = 0.0, min(d, 3.8)  # plan muet : court
        if b - a < 2.5:
            b = min(d, a + 2.5)
        fen.append((a, b, d))
    total = sum(b - a for a, b, _ in fen)
    if total < DUREE_MIN:
        # rendre du temps en fin de plan, proportionnellement à ce qui avait été coupé
        manque = DUREE_MIN - total
        dispo = [d - b for a, b, d in fen]
        somme = sum(dispo) or 1
        fen = [(a, min(d, b + manque * x / somme), d) for (a, b, d), x in zip(fen, dispo)]
    return [(round(a, 2), round(b, 2)) for a, b, _ in fen]

W, H, FPS = 1080, 1920, 30
EXT = {".mp4", ".mov", ".webm", ".mkv"}
COULEURS = ["&H00FFFFFF", "&H0000E5FF", "&H007CFF5B", "&H00FFC85A", "&H00A08CFF", "&H0066B3FF", "&H00F0A0FF"]


# ---------- 1. récupérer les clips ----------
def num(p):
    m = re.match(r"(\d+)", p.stem)
    return int(m.group(1)) if m else None


def recuperer_clips(dos, n, refaire):
    clips = dos / "clips"
    clips.mkdir(exist_ok=True)
    presents = [p for p in clips.iterdir() if p.suffix.lower() in EXT]
    if presents and not refaire:
        if all(num(p) is not None for p in presents):
            return sorted(presents, key=num)
        return sorted(presents, key=lambda p: p.stat().st_mtime)
    dl = Path.home() / "Downloads"
    recents = sorted((p for p in dl.iterdir() if p.suffix.lower() in EXT),
                     key=lambda p: p.stat().st_mtime, reverse=True)[:n]
    if len(recents) < n:
        raise SystemExit(f"Seulement {len(recents)} vidéos dans Téléchargements, il en faut {n}.")
    recents.reverse()  # ordre de téléchargement
    for p in presents:
        p.unlink()
    print("Clips pris dans Téléchargements (ordre de téléchargement) :")
    sortie = []
    for i, p in enumerate(recents, 1):
        cible = clips / f"{i:02d}{p.suffix.lower()}"
        shutil.copy2(p, cible)
        print(f"  {i:02d} <- {p.name}")
        sortie.append(cible)
    return sortie


# ---------- 2. normaliser ----------
def normaliser(clips, plans, dos, fenetres=None):
    norm = dos / "_norm"
    if norm.exists():
        shutil.rmtree(norm)
    norm.mkdir()
    sorties = []
    for i, c in enumerate(clips):
        garder = fenetres[i] if fenetres else None
        cmd = ["ffmpeg", "-hide_banner", "-y"]
        if garder:
            cmd += ["-ss", str(garder[0]), "-to", str(garder[1])]
        cmd += ["-i", str(c)]
        son = a_un_son(c)
        if not son:
            cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"fps={FPS},setsar=1,format=yuv420p")
        cmd += ["-vf", vf, "-map", "0:v:0", "-map", "0:a:0" if son else "1:a:0", "-shortest",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(norm / f"{i + 1:02d}.mp4")]
        run(cmd)
        sorties.append(norm / f"{i + 1:02d}.mp4")
    return sorties


# ---------- 3. sous-titres ----------
def ass_temps(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def couleur_perso(nom, ordre):
    if nom in ordre:
        return COULEURS[ordre.index(nom) % len(COULEURS)]
    h = int(hashlib.md5(nom.encode()).hexdigest(), 16)
    return COULEURS[h % len(COULEURS)]


def sous_titres(mots, bornes, plans, ep, sortie):
    ordre = ORDRE
    # qui parle dans chaque plan (une seule personne par plan)
    parleurs = [p.get("parle") if p.get("replique") else None for p in plans]

    def plan_de(t):
        for i, (a, b) in enumerate(bornes):
            if a <= t < b:
                return i
        return len(bornes) - 1

    groupes, cur = [], []
    for m in mots:
        if cur:
            gap = m["debut"] - cur[-1]["fin"]
            ponct = re.search(r"[.!?,…]$", cur[-1]["mot"])
            if len(cur) >= 3 or gap > 0.35 or ponct or plan_de(m["debut"]) != plan_de(cur[0]["debut"]):
                groupes.append(cur)
                cur = []
        cur.append(m)
    if cur:
        groupes.append(cur)

    lignes = []
    for i, g in enumerate(groupes):
        debut = g[0]["debut"]
        fin = g[-1]["fin"] + 0.15
        if i + 1 < len(groupes):
            fin = min(fin, groupes[i + 1][0]["debut"])
        texte = " ".join(w["mot"] for w in g).upper().replace("{", "").replace("}", "")
        pi = plan_de(debut)
        qui = parleurs[pi] if pi < len(parleurs) else None
        col = couleur_perso(qui, ordre) if qui else COULEURS[0]
        lignes.append(f"Dialogue: 0,{ass_temps(debut)},{ass_temps(fin)},Sub,,0,0,0,,"
                      f"{{\\1c{col}\\fscx82\\fscy82\\t(0,90,\\fscx100\\fscy100)}}{texte}")

    if ep.get("numero"):
        lignes.append(f"Dialogue: 1,{ass_temps(0)},{ass_temps(2.8)},Badge,,0,0,0,,"
                      f"{{\\fad(0,250)}}ÉPISODE {ep['numero']}")

    entete = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Arial Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,1,8,3,5,70,70,0,1
Style: Badge,Arial Black,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,2,0,1,5,0,8,60,60,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # position : un peu sous le centre, au-dessus de l'interface TikTok
    lignes = [l.replace(",Sub,,0,0,0,,{", ",Sub,,0,0,0,,{\\pos(540,1270)") for l in lignes]
    sortie.write_text(entete + "\n".join(lignes) + "\n", encoding="utf-8")
    return len(groupes)


# ---------- 4. musique ----------
def choisir_musique(ep):
    if not MUSIQUE.exists():
        return None
    pistes = sorted(p for p in MUSIQUE.iterdir() if p.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg"})
    if not pistes:
        return None
    if ep.get("musique"):
        for p in pistes:
            if p.name == ep["musique"]:
                return p
    h = int(hashlib.md5(str(ep.get("numero")).encode()).hexdigest(), 16)
    return pistes[h % len(pistes)]


# ---------- 5. couverture ----------
def couverture(video, t, titre, sortie):
    from PIL import Image, ImageDraw, ImageFont
    tmp = sortie.with_suffix(".tmp.jpg")
    run(["ffmpeg", "-hide_banner", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", str(tmp)])
    img = Image.open(tmp).convert("RGB")
    tmp.unlink()
    if titre:
        d = ImageDraw.Draw(img)
        mots, lignes, cur = titre.upper().split(), [], ""
        font = ImageFont.truetype(FONT_BOLD, 104)
        for m in mots:
            essai = (cur + " " + m).strip()
            if d.textlength(essai, font=font) > W - 140 and cur:
                lignes.append(cur)
                cur = m
            else:
                cur = essai
        lignes.append(cur)
        y = int(H * 0.30) - len(lignes) * 60
        for i, l in enumerate(lignes):
            col = "#FFE14D" if i == 0 else "white"
            w = d.textlength(l, font=font)
            d.text(((W - w) / 2, y), l, font=font, fill=col, stroke_width=10, stroke_fill="black")
            y += 124
    img.save(sortie, quality=92)


ORDRE = []


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projet")
    ap.add_argument("episode", nargs="?", default="ep001")
    ap.add_argument("--refaire", action="store_true")
    ap.add_argument("--sans-musique", action="store_true")
    ap.add_argument("--garder-sous-titres", action="store_true",
                    help="réutilise sous-titres.ass corrigé à la main")
    ap.add_argument("--sans-rythme", action="store_true", help="garde les clips Grok entiers")
    a = ap.parse_args()

    global ORDRE
    b = Bible(a.projet)
    ORDRE = b.ordre
    dos = b.episodes / a.episode
    ep = lire_json(dos / "episode.json")
    plans = [compat_plan(p) for p in ep["plans"]]
    clips = recuperer_clips(dos, len(plans), a.refaire)
    if len(clips) != len(plans):
        print(f"ATTENTION : {len(clips)} clips pour {len(plans)} plans.")

    fen = None
    if not a.sans_rythme:
        print("0/5 rythme : on coupe les silences de début et fin de clip…")
        fen = rythme(clips, plans, dos)
        print("   " + "  ".join(f"{i + 1:02d}:{b - x:.1f}s" for i, (x, b) in enumerate(fen)))
    print("1/5 normalisation des clips…")
    norm = normaliser(clips, plans, dos, fen)
    durees = [duree(p) for p in norm]
    bornes, t = [], 0.0
    for d in durees:
        bornes.append((t, t + d))
        t += d

    print("2/5 assemblage…")
    (dos / "_norm" / "liste.txt").write_text("".join(f"file '{p.name}'\n" for p in norm), encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0", "-i", "liste.txt",
         "-c", "copy", "../_assemble.mp4"], cwd=dos / "_norm")
    assemble = dos / "_assemble.mp4"

    print("3/5 sous-titres (whisper)…")
    wav = dos / "_voix.wav"
    run(["ffmpeg", "-hide_banner", "-y", "-i", str(assemble), "-ac", "1", "-ar", "16000", str(wav)])
    dialogue = " ".join(p["replique"] for p in plans if p.get("replique"))
    tr = whisper(wav, langue="fr", prompt=dialogue[:800])
    wav.unlink()
    if a.garder_sous_titres and (dos / "sous-titres.ass").exists():
        nb_sub = (dos / "sous-titres.ass").read_text(encoding="utf-8").count("Dialogue:")
        print("   sous-titres.ass existant conservé")
    else:
        nb_sub = sous_titres(tr["mots"], bornes, plans, ep, dos / "sous-titres.ass")

    print("4/5 mixage et rendu final…")
    musique = None if a.sans_musique else choisir_musique(ep)
    final = dos / f"{a.episode}_final.mp4"
    total = bornes[-1][1]
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", "_assemble.mp4"]
    if musique:
        cmd += ["-stream_loop", "-1", "-i", str(musique)]
        af = ("[0:a]asplit=2[voix][cle];"
              "[1:a]volume=0.22,aformat=sample_rates=48000:channel_layouts=stereo[mus];"
              "[mus][cle]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[musd];"
              f"[voix][musd]amix=inputs=2:duration=first:normalize=0,atrim=0:{total:.3f}")
    else:
        af = "[0:a]anull"
    mesure = run(cmd + ["-filter_complex", af + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-vn", "-f", "null", "-"], cwd=dos)
    js = mesure[mesure.rindex("{"):mesure.rindex("}") + 1]
    import json
    m = json.loads(js)
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(cmd + ["-filter_complex", f"[0:v]ass=sous-titres.ass[v];{af},{ln},aresample=48000[a]",
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow",
               "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
               "-movflags", "+faststart", final.name], cwd=dos)

    print("5/5 couverture, publication, rapport…")
    t_cov = (bornes[0][0] + bornes[0][1]) / 2
    couverture(final, t_cov, ep.get("titre_couverture"), dos / "couverture.jpg")
    pub = [ep.get("legende", ""), "", " ".join(ep.get("hashtags", [])), "",
           "COMMENTAIRE À ÉPINGLER :", ep.get("commentaire_epingle", ""), "",
           "RAPPEL : activer l'étiquette « contenu généré par IA »."]
    (dos / "publication.txt").write_text("\n".join(pub), encoding="utf-8")

    # contrôles
    lufs = run(["ffmpeg", "-hide_banner", "-i", str(final), "-af", "ebur128=peak=true", "-f", "null", "-"])
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", lufs)[-1]
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", lufs)[-1]
    fr = run(["ffmpeg", "-hide_banner", "-i", str(final), "-vf", "freezedetect=n=-55dB:d=1.5",
              "-map", "0:v:0", "-f", "null", "-"])
    gels = re.findall(r"freeze_start: ([\d.]+)", fr)
    sans_son = [i + 1 for i, c in enumerate(clips) if not a_un_son(c)]
    mots_script = len(dialogue.split())
    couverture_dialogue = round(len(tr["mots"]) / mots_script * 100) if mots_script else 0
    dfin = duree(final)

    def ligne(ok, regle, mesure_):
        return f"| {'OK' if ok else 'ATTENTION'} | {regle} | {mesure_} |"

    rap = ["# Rapport de montage", "", "| Résultat | Contrôle | Mesure |", "|---|---|---|",
           ligne(len(clips) == len(plans), "Un clip par plan", f"{len(clips)} clips / {len(plans)} plans"),
           ligne(60 <= dfin <= 80, "Durée 60 à 80 s (Creator Rewards > 60 s)", f"{dfin:.1f} s"),
           ligne(abs(float(I) + 14) <= 1, "Volume -14 LUFS", f"{I} LUFS, crête {tp} dBFS"),
           ligne(not gels, "Aucune image figée > 1,5 s", ", ".join(f"{float(g):.1f}s" for g in gels) or "aucune"),
           ligne(not sans_son, "Tous les clips ont du son", ", ".join(map(str, sans_son)) or "oui"),
           ligne(couverture_dialogue >= 70, "Grok a dit les répliques (mots entendus / écrits)",
                 f"{couverture_dialogue} %"),
           ligne(True, "Sous-titres", f"{nb_sub} blocs"),
           ligne(bool(musique), "Musique de fond", musique.name if musique else "aucune (dossier musique/ vide)"),
           "", "À vérifier à l'œil : l'ordre des plans, les personnages identiques d'un plan à l'autre, "
           "l'orthographe des sous-titres (corrigeable dans sous-titres.ass puis relancer)."]
    (dos / "rapport.md").write_text("\n".join(rap), encoding="utf-8")
    assemble.unlink()
    shutil.rmtree(dos / "_norm")
    # version téléphone : < 19 Mo pour passer par la page Studio
    tel = dos / f"{a.episode}_tel.mp4"
    kbps = int(18.5 * 8 * 1024 / dfin) - 160
    run(["ffmpeg", "-hide_banner", "-y", "-i", str(final), "-c:v", "libx264", "-profile:v", "high",
         "-preset", "slow", "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.2)}k", "-bufsize", f"{kbps * 2}k",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(tel)])
    print("\n".join(rap))
    print(f"\nVIDÉO : {final}\nVERSION TÉLÉPHONE : {tel} ({tel.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()
