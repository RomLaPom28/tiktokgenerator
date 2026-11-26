"""Outils communs du studio : chemins, ffmpeg, whisper."""
import json
import subprocess
import sys
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

STUDIO = Path(__file__).resolve().parent.parent
SOURCES = STUDIO / "sources"
ANALYSES = STUDIO / "analyses"
BIBLE = STUDIO / "bible"          # commun à tous les projets : realisation, conformite, recettes, concepts
PROJETS = STUDIO / "projets"      # un dossier par vidéo unique ou par série
MUSIQUE = STUDIO / "musique"

FONT_BOLD = "C:/Windows/Fonts/ariblk.ttf"


def run(cmd, **kw):
    """Lance une commande, renvoie stdout+stderr, lève une erreur lisible si échec."""
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        print("ERREUR commande :", " ".join(str(c) for c in cmd), file=sys.stderr)
        print(r.stderr[-3000:], file=sys.stderr)
        raise SystemExit(1)
    return r.stdout + r.stderr


def duree(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.strip().splitlines()[0])


def a_un_son(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
               "-of", "csv=p=0", str(path)])
    return bool(out.strip())


def args_projet(argv):
    """`<projet> [epNNN]` -> (projet, episode). Épisode par défaut : ep001 (vidéo unique)."""
    pos = [a for a in argv if not a.startswith("--")]
    if not pos:
        raise SystemExit("Usage : <projet> [epNNN]   (ex. : la-ferme ep003, ou mon-projet pour une vidéo unique)")
    return pos[0], (pos[1] if len(pos) > 1 else "ep001")


def lire_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ecrire_json(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


_modele = None


def whisper(audio, langue=None, prompt=None):
    """Transcription mot par mot. GPU si possible, sinon CPU."""
    global _modele
    import os
    try:  # DLL CUDA installées par pip (nvidia-cublas-cu12, nvidia-cudnn-cu12)
        import nvidia.cublas
        import nvidia.cudnn
        for pkg in (nvidia.cublas, nvidia.cudnn):
            b = Path(list(pkg.__path__)[0]) / "bin"
            if b.exists():
                os.add_dll_directory(str(b))
                os.environ["PATH"] = str(b) + os.pathsep + os.environ["PATH"]
    except ImportError:
        pass
    from faster_whisper import WhisperModel
    if _modele is None:
        try:
            _modele = WhisperModel("medium", device="cuda", compute_type="float16")
            # test rapide : certaines installs CUDA plantent seulement à l'usage
            list(_modele.transcribe(str(audio), language=langue, word_timestamps=True)[0])[:1]
        except Exception as e:  # noqa: BLE001
            print(f"(GPU indisponible pour whisper : {str(e)[:120]} -> CPU)")
            _modele = WhisperModel("small", device="cpu", compute_type="int8")
    src = str(audio)
    if src.endswith(".wav"):  # wav 16 kHz mono : lecture directe (évite un conflit de version PyAV)
        import wave
        import numpy as np
        with wave.open(src, "rb") as wv:
            src = np.frombuffer(wv.readframes(wv.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    segs, info = _modele.transcribe(src, language=langue, word_timestamps=True,
                                    initial_prompt=prompt, vad_filter=True)
    mots, phrases = [], []
    for s in segs:
        phrases.append({"debut": round(s.start, 2), "fin": round(s.end, 2), "texte": s.text.strip()})
        for w in (s.words or []):
            mots.append({"debut": round(w.start, 2), "fin": round(w.end, 2), "mot": w.word.strip()})
    return {"langue": info.language, "phrases": phrases, "mots": mots}


# ---------- plans : ancien format (replique/parle) et nouveau format (duree + timeline) ----------
def duree_plan(p):
    """Durée du clip Grok : 6 ou 10 s (défaut 6)."""
    return int(p.get("duree", 6))


def dialogues(p):
    """Liste [{t, parle, emotion, texte}] ; convertit l'ancien format (une seule réplique)."""
    if p.get("dialogues"):
        return p["dialogues"]
    if p.get("replique"):
        return [{"t": f"0-{duree_plan(p)}", "parle": p.get("parle"), "emotion": p.get("emotion", ""),
                 "texte": p["replique"]}]
    return []


def texte_plan(p):
    return " ".join(d["texte"] for d in dialogues(p))


def parleurs(p):
    vus = []
    for d in dialogues(p):
        if d.get("parle") and d["parle"] not in vus:
            vus.append(d["parle"])
    return vus


def compat_plan(p):
    """Ajoute replique/parle (format attendu par monter.py) à un plan du nouveau format."""
    q = dict(p)
    q["replique"] = texte_plan(p)
    q["parle"] = (parleurs(p) or [None])[0]
    return q
