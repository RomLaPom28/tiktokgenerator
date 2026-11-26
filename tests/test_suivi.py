"""Tests du suivi des performances (outils/suivi.py).

Lancer depuis la racine :  python3 -m unittest discover -s tests -v
Tout se passe dans un dossier temporaire (copie des projets, du registre des mécaniques et un stats.csv inventé) :
les vrais fichiers ne sont jamais modifiés. Les chiffres ci-dessous sont des données de test, pas des résultats.
"""
import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import mecaniques  # noqa: E402
import suivi  # noqa: E402

ENTETE = ";".join(suivi.COLONNES)
MECAS = {  # mécaniques déclarées dans les copies des épisodes (les vrais épisodes n'en ont pas encore)
    "prodige-34-ans/ep001": ["ironie_dramatique", "chiffre_ecran"],
    "ecrase-la/ep001": ["ironie_dramatique", "renversement_statut"],
    "bagagiste-honnete/ep001": ["ironie_dramatique", "coupure_avant_payoff"],
    "bagagiste-honnete/ep002": ["temoin_reaction"],
    "faux-joueur-district/ep001": ["epreuve_verdict"],
}


def ligne(projet, ep, pub, rel, vues="", com="", **autres):
    d = {"projet": projet, "episode": ep, "plateforme": "tiktok", "date_publication": pub, "date_releve": rel,
         "vues": vues, "commentaires": com, **autres}
    return ";".join(str(d.get(c, "")) for c in suivi.COLONNES)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(RACINE / "projets", self.tmp / "projets")
        for k, v in MECAS.items():
            proj, ep = k.split("/")
            f = self.tmp / "projets" / proj / "episodes" / ep / "episode.json"
            e = json.loads(f.read_text(encoding="utf-8"))
            e["mecaniques_utilisees"] = v
            f.write_text(json.dumps(e, ensure_ascii=False), encoding="utf-8")
        self.reg = self.tmp / "mecaniques.json"
        shutil.copy(RACINE / "bible" / "mecaniques.json", self.reg)
        self.csv = self.tmp / "stats.csv"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ecrire(self, *lignes, encodage="utf-8", entete=ENTETE):
        self.csv.write_bytes(("\n".join((entete,) + lignes) + "\n").encode(encodage))

    def charger(self):
        return suivi.charger(self.csv, self.tmp / "projets")

    def jeu_complet(self):
        """6 publications, 5 projets, relevés à J+7 (et un J+2 seul pour la-ferme)."""
        self.ecrire(
            ligne("prodige-34-ans", "ep001", "2026-11-01", "2026-11-08", "120 000", "850", likes="9000", completion_pct="38", temps_moyen_s="31,5", duree_s="72"),
            ligne("ecrase-la", "ep001", "2026-11-03", "2026-11-10", "90000", "600"),
            ligne("bagagiste-honnete", "ep001", "2026-11-05", "2026-11-12", "80000", "1200", completion_pct="45"),
            ligne("bagagiste-honnete", "ep002", "2026-11-08", "2026-11-15", "20000", "300"),
            ligne("faux-joueur-district", "ep001", "2026-11-12", "2026-11-19", "9000", "15"),
            ligne("prodige-34-ans", "ep001", "2026-11-01", "2026-11-03", "40000", "200"),
            ligne("la-ferme", "ep001", "2026-11-15", "2026-11-17", "3000", "5"),
        )
        pubs, err = self.charger()
        self.assertEqual(err, [])
        return pubs


# ---------------------------------------------------------------- saisie
class Saisie(Base):
    def test_nombres_et_absences(self):
        n = suivi._nombre
        self.assertEqual(n("12 300", "vues", True), 12300)
        self.assertEqual(n("12 300", "vues", True), 12300)
        self.assertEqual(n("31,5", "temps_moyen_s", False), 31.5)
        self.assertEqual(n("0:40", "temps_moyen_s", False), 40)
        self.assertEqual(n("45 %", "completion_pct", False), 45)
        self.assertIsNone(n("", "vues", True))
        self.assertIsNone(n("—", "revenus_eur", False))
        with self.assertRaises(suivi.ErreurSaisie):
            n("12,3K", "vues", True)      # arrondi d'appli : refusé, jamais converti
        with self.assertRaises(suivi.ErreurSaisie):
            n("12,5", "vues", True)

    def test_donnees_manquantes_restent_nulles(self):
        self.ecrire(ligne("prodige-34-ans", "ep001", "2026-11-01", "2026-11-08", "1000"))
        pubs, err = self.charger()
        M = suivi.mesures(pubs, 7)
        m = M["prodige-34-ans/ep001/tiktok"]
        for k in ("taux_commentaires", "taux_likes", "completion_pct", "part_regardee", "revenus_1000", "abonnes_1000", "indice_vues"):
            self.assertIsNone(m[k], k)
        self.assertIsNone(pubs["prodige-34-ans/ep001/tiktok"]["duree_s"])   # jamais la durée des rushs

    def test_erreurs_de_saisie(self):
        self.ecrire(
            ligne("inconnu", "ep001", "2026-11-01", "2026-11-08", "10"),
            ligne("prodige-34-ans", "ep001", "2026-11-08", "2026-11-01", "10"),
            ligne("ecrase-la", "ep001", "2026-11-01", "2026-11-08", "10", completion_pct="140"),
            ligne("ecrase-la", "ep001", "2026-11-01", "2026-11-09", "10", "50"),
            ligne("bagagiste-honnete", "ep001", "2026-11-01", "2026-11-08", "10"),
            ligne("bagagiste-honnete", "ep001", "2026-11-02", "2026-11-09", "10"),
            ligne("bagagiste-honnete", "ep002", "2026-11-01", "2026-11-08", "10"),
            ligne("bagagiste-honnete", "ep002", "2026-11-01", "2026-11-08", "12"),
        )
        _, err = self.charger()
        texte = " | ".join(err)
        for attendu in ("épisode inconnu", "avant date_publication", "pourcentage", "colonnes inversées",
                        "date_publication différente", "deux relevés"):
            self.assertIn(attendu, texte)

    def test_csv_excel_windows(self):
        self.ecrire(ligne("prodige-34-ans", "ep001", "01/11/2026", "08/11/2026", "1 000", notes="vidéo très appréciée"),
                    encodage="cp1252")
        pubs, err = self.charger()
        self.assertEqual(err, [])
        self.assertEqual(pubs["prodige-34-ans/ep001/tiktok"]["releves"][0]["vues"], 1000)

    def test_csv_separateur_virgule(self):
        self.csv.write_text("projet,episode,date_publication,date_releve,vues\nprodige-34-ans,ep001,2026-11-01,2026-11-08,500\n",
                            encoding="utf-8")
        pubs, err = self.charger()
        self.assertEqual(err, [])
        self.assertEqual(len(pubs), 1)

    def test_duree_lue_dans_le_rapport_de_montage(self):
        dos = self.tmp / "projets" / "ecrase-la" / "episodes" / "ep001"
        (dos / "rapport.md").write_text("| OK | Durée 60 à 80 s (Creator Rewards > 60 s) | 71.4 s |", encoding="utf-8")
        self.ecrire(ligne("ecrase-la", "ep001", "2026-11-01", "2026-11-08", "10"))
        pubs, _ = self.charger()
        self.assertEqual(pubs["ecrase-la/ep001/tiktok"]["duree_s"], 71.4)
        self.assertEqual(pubs["ecrase-la/ep001/tiktok"]["tranche"], "60-75 s")

    def test_commande_ajouter(self):
        ancien = suivi.STATS
        suivi.STATS = self.tmp / "suivi" / "stats.csv"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                suivi.main(["ajouter", "prodige-34-ans", "--publie", "2026-11-01", "--releve", "2026-11-08",
                            "--vues", "1000", "--commentaires", "12", "--completion", "41,5"])
                with self.assertRaises(SystemExit):   # refusée : rien n'est écrit
                    suivi.main(["ajouter", "prodige-34-ans", "--publie", "2026-11-01", "--releve", "2026-11-09", "--vues", "3K"])
            lignes = suivi.lire_csv(suivi.STATS)
            self.assertEqual(len(lignes), 1)
            self.assertEqual(lignes[0][1]["completion_pct"], "41,5")
            self.assertEqual(lignes[0][1]["likes"], "")
            self.assertFalse(list(suivi.STATS.parent.glob("*.tmp.csv")))
        finally:
            suivi.STATS = ancien


# ---------------------------------------------------------------- analyse
class Analyse(Base):
    def test_meme_age_et_exclusions(self):
        pubs = self.jeu_complet()
        M7 = suivi.mesures(pubs, 7)
        self.assertNotIn("la-ferme/ep001/tiktok", M7)                  # relevé à J+2 seulement
        self.assertEqual(M7["prodige-34-ans/ep001/tiktok"]["vues"], 120000)  # le relevé J+7, pas J+2
        M2 = suivi.mesures(pubs, 2)
        self.assertEqual(M2["prodige-34-ans/ep001/tiktok"]["vues"], 40000)
        self.assertIn("la-ferme/ep001/tiktok", M2)

    def test_vues_relatives_au_compte(self):
        pubs = self.jeu_complet()
        M = suivi.mesures(pubs, 7)
        # médiane des autres : (90000, 80000, 20000, 9000) → 50000
        self.assertEqual(M["prodige-34-ans/ep001/tiktok"]["indice_vues"], 2.4)

    def test_mecaniques_non_renseignees_ni_avec_ni_sans(self):
        pubs = self.jeu_complet()
        pubs["ecrase-la/ep001/tiktok"]["mecaniques"] = None
        M = suivi.mesures(pubs, 7)
        g = suivi.comparer_groupe(pubs, M, lambda p: None if p["mecaniques"] is None else "ironie_dramatique" in p["mecaniques"])
        self.assertEqual(g["n_avec"] + g["n_sans"], len(M) - 1)

    def test_une_video_reste_une_hypothese(self):
        pubs = self.jeu_complet()
        M = suivi.mesures(pubs, 7)
        g = suivi.comparer_groupe(pubs, M, lambda p: "chiffre_ecran" in (p["mecaniques"] or []))
        self.assertEqual(g["n_avec"], 1)
        self.assertTrue(g["confiance"].startswith("hypothèse"))
        self.assertTrue(g["confusions"])            # tout est confondu avec cette vidéo-là

    def test_signal_repete_exige_trois_projets_concordants(self):
        pubs = self.jeu_complet()
        M = suivi.mesures(pubs, 7)
        g = suivi.comparer_groupe(pubs, M, lambda p: "ironie_dramatique" in (p["mecaniques"] or []))
        self.assertEqual((g["n_avec"], g["projets_avec"]), (3, 3))
        self.assertEqual(g["sens"], "mieux")
        self.assertEqual(g["confiance"], "signal répété")
        # même chiffres mais 2 vidéos d'un même projet : reste une hypothèse
        pubs2 = copy.deepcopy(pubs)
        pubs2["ecrase-la/ep001/tiktok"]["projet"] = "prodige-34-ans"
        g2 = suivi.comparer_groupe(pubs2, M, lambda p: "ironie_dramatique" in (p["mecaniques"] or []))
        self.assertTrue(g2["confiance"].startswith("hypothèse"))

    def test_variable_confondue_empeche_le_signal(self):
        pubs = self.jeu_complet()
        for q in ("prodige-34-ans/ep001/tiktok", "ecrase-la/ep001/tiktok", "bagagiste-honnete/ep001/tiktok"):
            pubs[q]["accroche"] = "aveu"
        for q in ("bagagiste-honnete/ep002/tiktok", "faux-joueur-district/ep001/tiktok"):
            pubs[q]["accroche"] = "menace"
        M = suivi.mesures(pubs, 7)
        g = suivi.comparer_groupe(pubs, M, lambda p: "ironie_dramatique" in (p["mecaniques"] or []))
        self.assertIn("type de hook = aveu", g["confusions"])
        self.assertNotEqual(g["confiance"], "signal répété")

    def test_rapport_six_rubriques_et_prudence(self):
        pubs = self.jeu_complet()
        M = suivi.mesures(pubs, 7)
        t = suivi.rapport(pubs, M, 7)
        for rub in ("## 1. Ce qui fonctionne le mieux", "## 2. Ce qui fonctionne moins bien", "## 3. Hypothèses à tester",
                    "## 4. Mécaniques à réutiliser", "## 5. Mécaniques à éviter ou à retravailler",
                    "## 6. Prochaines expériences recommandées", "Annexe A"):
            self.assertIn(rub, t)
        self.assertIn("la-ferme/ep001/tiktok (relevés à J+2)", t)
        self.assertNotRegex(t, r"(?i)\b(grâce à|à cause de|cause les|provoque)\b")
        self.assertIn("pas à éviter", t)            # epreuve_verdict : 1 vidéo faible ≠ mécanique à éviter

    def test_rapport_trop_peu_de_donnees(self):
        self.ecrire(ligne("prodige-34-ans", "ep001", "2026-11-01", "2026-11-08", "1000"))
        pubs, _ = self.charger()
        t = suivi.rapport(pubs, suivi.mesures(pubs, 7), 7)
        self.assertIn("Trop peu de publications comparables", t)

    def test_comparer_deux(self):
        pubs = self.jeu_complet()
        t = suivi.comparer_deux(pubs, "prodige-34-ans/ep001/tiktok", "ecrase-la/ep001/tiktok", 7)
        self.assertIn("ne s'attribue à aucune", t)


# ---------------------------------------------------------------- apprentissage
class Apprentissage(Base):
    def test_ecrit_seulement_le_bloc_calcule(self):
        avant = json.loads(self.reg.read_text(encoding="utf-8"))
        pubs = self.jeu_complet()
        M = suivi.mesures(pubs, 7)
        suivi.apprendre(pubs, M, 7, "2026-11-26", self.reg)
        apres = json.loads(self.reg.read_text(encoding="utf-8"))
        rp = {m["id"]: m.get("resultats_propres") for m in apres["mecaniques"]}
        self.assertEqual(rp["chiffre_ecran"]["confiance"], "hypothèse (1 seule vidéo)")
        self.assertEqual(rp["ironie_dramatique"]["confiance"], "signal répété")
        self.assertIsNone(rp["regle_du_monde"])                    # jamais utilisée : pas de bloc
        for a, b in zip(avant["mecaniques"], apres["mecaniques"]):  # aucun autre champ touché (preuves du corpus incluses)
            b = {k: v for k, v in b.items() if k != "resultats_propres"}
            self.assertEqual(a, b)
        self.assertEqual(avant["contradictions"], apres["contradictions"])
        self.assertEqual(avant["_regles"], apres["_regles"])

    def test_sans_mecaniques_ne_touche_pas_au_fichier(self):
        avant = self.reg.read_bytes()
        self.ecrire(ligne("la-ferme", "ep001", "2026-11-01", "2026-11-08", "1000"),
                    ligne("la-ferme", "ep002", "2026-11-02", "2026-11-09", "2000"))
        pubs, _ = self.charger()
        suivi.apprendre(pubs, suivi.mesures(pubs, 7), 7, registre_chemin=self.reg)
        self.assertEqual(self.reg.read_bytes(), avant)

    def test_registre_toujours_valide_pour_mecaniques_py(self):
        pubs = self.jeu_complet()
        suivi.apprendre(pubs, suivi.mesures(pubs, 7), 7, registre_chemin=self.reg)
        ancien = mecaniques.REGISTRE
        mecaniques.REGISTRE = self.reg
        try:
            registre, reg = mecaniques.charger_registre()
            erreurs, _ = mecaniques.verifier(registre, reg, mecaniques.charger_corpus())
        finally:
            mecaniques.REGISTRE = ancien
        self.assertEqual(erreurs, [])
        self.assertIn("resultats_propres", reg["ironie_dramatique"])


if __name__ == "__main__":
    unittest.main()
