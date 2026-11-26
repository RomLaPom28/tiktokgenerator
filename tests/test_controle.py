"""Tests du contrôle qualité (outils/verifier.py + outils/doctor.py).

Lancer depuis la racine :  python3 -m unittest discover -s tests -v
(PC Windows : python -m unittest discover -s tests -v). Aucune dépendance hors bibliothèque standard.
Chaque test travaille sur une COPIE d'un projet dans un dossier temporaire : les vrais projets ne sont jamais modifiés.
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

import bible  # noqa: E402
import commun  # noqa: E402
import doctor  # noqa: E402
import verifier  # noqa: E402

VRAIS_PROJETS = commun.PROJETS
EPISODES_EXISTANTS = sorted((p.parent.parent.parent.name, p.parent.name) for p in VRAIS_PROJETS.glob("*/episodes/*/episode.json"))


def niveaux(res, rid):
    return [x["niveau"] for x in res if x["id"] == rid]


class BaseProjet(unittest.TestCase):
    """Copie projets/<SOURCE> dans un dossier temporaire et y redirige bible.py."""
    SOURCE = "prodige-34-ans"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(VRAIS_PROJETS / self.SOURCE, self.tmp / self.SOURCE)
        self._ancien = bible.PROJETS
        bible.PROJETS = self.tmp
        self.dossier = self.tmp / self.SOURCE
        self.f_ep = self.dossier / "episodes" / "ep001" / "episode.json"
        self.ep = json.loads(self.f_ep.read_text(encoding="utf-8"))

    def tearDown(self):
        bible.PROJETS = self._ancien
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ecrire(self, ep=None, **projet):
        self.f_ep.write_text(json.dumps(ep or self.ep, ensure_ascii=False), encoding="utf-8")
        if projet:
            f = self.dossier / "projet.json"
            pj = json.loads(f.read_text(encoding="utf-8"))
            pj.update(projet)
            f.write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

    def verifier(self):
        return verifier.verifier(self.SOURCE, "ep001")

    def echecs(self, res):
        return [x["id"] for x in res if x["niveau"] == "ÉCHEC"]

    def revue_complete(self, **surcharge):
        r = doctor.modele_revue(self.ep)
        for k in r["grille"]:
            r["grille"][k] = {"note": "valide", "constat": "vu au plan 1", "correction": ""}
        r.update(date="2026-11-24", independant=True, verdict="solide", points_forts=["hook net"], resume="ok")
        r.update(surcharge)
        return r


# ---------------------------------------------------------------- compatibilité des anciens projets
class AnciensProjets(unittest.TestCase):
    def test_tous_les_episodes_existants_passent_le_controle_technique(self):
        self.assertTrue(EPISODES_EXISTANTS)
        for projet, ep in EPISODES_EXISTANTS:
            with self.subTest(projet=projet, ep=ep):
                res, ctx = verifier.verifier(projet, ep)
                bloquants = [f"{x['regle']} — {x['mesure']}" for x in res if x["niveau"] == "ÉCHEC"]
                self.assertEqual(bloquants, [], f"{projet} {ep}")
                self.assertIn("OK", niveaux(res, "compat_pack"))

    def test_rapport_complet_sans_plantage(self):
        for projet, ep in EPISODES_EXISTANTS:
            with self.subTest(projet=projet, ep=ep):
                res, ctx = verifier.verifier(projet, ep)
                d = verifier.decision(res, ctx, ep)
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    verifier.afficher(res, d, ctx, ep, detail=True)
                texte = out.getvalue()
                for rubrique in ("VERDICT TECHNIQUE", "VERDICT ÉDITORIAL", "1. ERREURS BLOQUANTES", "2. AMÉLIORATIONS",
                                 "3. POINTS FORTS", "4. RISQUES DE PRODUCTION", "5. VERDICT ÉDITORIAL"):
                    self.assertIn(rubrique, texte)

    def test_registre_complet(self):
        reg = doctor.controles()["regles"]
        for rid, r in reg.items():
            self.assertIn(r["nature"], ("technique", "editorial", "preference"), rid)
            self.assertTrue(r.get("nom"), rid)
        source = (RACINE / "outils" / "verifier.py").read_text(encoding="utf-8")
        import re
        utilises = set(re.findall(r'ok\("([a-z0-9_]+)"', source)) | set(re.findall(r'echec\("([a-z0-9_]+)"', source))
        self.assertFalse(utilises - set(reg), "contrôles utilisés mais absents de bible/controles.json")


# ---------------------------------------------------------------- contrôles techniques
class Technique(BaseProjet):
    def test_json_invalide_ne_plante_pas(self):
        self.f_ep.write_text("{ pas du json", encoding="utf-8")
        res, ctx = self.verifier()
        self.assertEqual(self.echecs(res), ["json_valide"])
        self.assertIsNone(ctx["ep"])

    def test_champ_obligatoire_manquant(self):
        del self.ep["plans"][2]["lieu"]
        self.ecrire()
        res, _ = self.verifier()
        self.assertIn("champs_obligatoires", self.echecs(res))

    def test_numerotation(self):
        self.ep["plans"][3]["n"] = 99
        self.ecrire()
        self.assertIn("numerotation_plans", self.echecs(self.verifier()[0]))

    def test_personnage_et_lieu_inconnus(self):
        self.ep["plans"][1]["persos"][0]["id"] = "fantome"
        self.ep["plans"][2]["lieu"] = "lune"
        self.ecrire()
        e = self.echecs(self.verifier()[0])
        self.assertIn("persos_existants", e)
        self.assertIn("lieux_existants", e)

    def test_parleur_hors_champ_inconnu_bloque_au_lieu_de_casser_pack(self):
        self.ep["plans"][0]["dialogues"][0].update(parle="inconnu", hors_champ=True)
        self.ecrire()
        self.assertIn("persos_existants", self.echecs(self.verifier()[0]))

    def test_timecodes_duree_image_de_fin_debit(self):
        p = self.ep["plans"][0]
        p["dialogues"][0]["t"] = "5-9"                       # hors des 6 s
        p["dialogues"][1]["texte"] = "un deux trois quatre cinq six sept huit neuf dix onze"
        p["dialogues"][1]["t"] = "2.5-3.0"                    # 22 mots/s
        q = next(x for x in self.ep["plans"] if x.get("duree") == 10)
        del q["fin"]
        self.ep["plans"][1]["duree"] = 8
        self.ecrire()
        e = self.echecs(self.verifier()[0])
        for rid in ("timecodes", "debit_parle", "image_fin_10s", "durees_grok"):
            self.assertIn(rid, e)

    def test_conformite_reste_bloquante(self):
        self.ep["plans"][3]["dialogues"][0]["texte"] = "Espèce de bâtard"
        self.ep["plans"][3]["replique"] = "Espèce de bâtard"
        self.ecrire()
        self.assertIn("conformite_rouge", self.echecs(self.verifier()[0]))

    def test_compat_pack_assemble_tous_les_prompts(self):
        b = bible.Bible(self.SOURCE)
        ok, mesure = verifier.compat_pack(b, self.ep)
        self.assertTrue(ok, mesure)
        # un code que pack.py ne sait pas traduire casse l'assemblage
        ep = copy.deepcopy(self.ep)
        ep["plans"][0]["lumiere"] = "inconnue"
        ok, mesure = verifier.compat_pack(b, ep)
        self.assertFalse(ok)
        self.assertIn("plan 1", mesure)

    def test_moteur_obligatoire_pour_nouveau_projet(self):
        self.ep.pop("moteur")
        self.ep["controle"] = 2
        self.ecrire()
        self.assertIn("moteur_socle", self.echecs(self.verifier()[0]))

    def test_moteur_absent_sur_ancien_episode_signale_sans_bloquer(self):
        self.ep.pop("moteur")
        for p in self.ep["plans"]:
            for d in p.get("dialogues", []):
                d.pop("fonction", None)
        self.ecrire()
        res, _ = self.verifier()
        self.assertNotIn("moteur_socle", self.echecs(res))
        self.assertIn("À VOIR", niveaux(res, "moteur_socle"))
        self.assertIn("À VOIR", niveaux(res, "fonction_repliques"))

    def test_projet_creer_v3_exige_histoire_validee(self):
        self.ecrire(creer=3)
        self.assertIn("histoire_validee", self.echecs(self.verifier()[0]))
        (self.dossier / "histoire.json").write_text(json.dumps({"choix": "A", "variantes": [{"id": "A", "motivations": []}]}),
                                                    encoding="utf-8")
        self.assertNotIn("histoire_validee", self.echecs(self.verifier()[0]))


# ---------------------------------------------------------------- règles assouplies
class Assouplissement(BaseProjet):
    def test_regles_de_rythme_ne_bloquent_jamais(self):
        for p in self.ep["plans"]:
            p["camera"] = "fixe"
            p["cadrage"] = "GP"
            p["angle"] = "face"
            p.pop("timeline", None)
            p["mouvement"] = "il regarde"
            ds = p.get("dialogues") or []
            if ds:  # un seul parleur, une seule réplique courte en début de plan : long silence, pas de ping-pong
                p["dialogues"] = [dict(ds[0], t="2.5-3.0", parle=ds[0]["parle"], fonction="reaction", texte="Quoi ?")]
        for p in self.ep["plans"]:
            if p.get("role") == "retournement":
                p["role"] = "developpement"
        self.ep.pop("question_milieu")
        self.ecrire()
        res, _ = self.verifier()
        self.assertEqual(self.echecs(res), [])
        for rid in ("parole_part", "silence_max", "pingpong", "clashs", "cameras_variees", "cadrage_repete",
                    "retournements_positions", "temps_forts", "question_milieu"):
            self.assertIn("À VOIR", niveaux(res, rid), rid)
            self.assertEqual(next(x["nature"] for x in res if x["id"] == rid), "preference", rid)

    def test_plan_muet_declare_ne_compte_pas_comme_silence(self):
        p = self.ep["plans"][5]
        p["dialogues"] = [dict(p["dialogues"][0], t="0.1-0.8", texte="Non.")]
        p["muet"] = "face-à-face : le silence porte la menace"
        self.ecrire()
        res, _ = self.verifier()
        trous = [x["mesure"] for x in res if x["id"] == "silence_max"]
        self.assertNotIn("6:", str(trous))

    def test_choix_creatif_assume(self):
        self.ep["choix_creatifs"] = {"pingpong": "huis clos à un seul personnage", "debit_parle": "essai"}
        for p in self.ep["plans"]:
            if len(p.get("dialogues", [])) > 1:
                p["dialogues"] = p["dialogues"][:1]
        self.ep["plans"][0]["dialogues"][0]["t"] = "0.1-0.5"  # débit trop rapide : technique, non contournable
        self.ecrire()
        res, _ = self.verifier()
        self.assertEqual(niveaux(res, "pingpong"), ["CHOIX"])
        self.assertEqual(niveaux(res, "debit_parle"), ["ÉCHEC"])

    def test_premiere_replique_tardive_nest_plus_bloquante(self):
        self.ep["plans"][0]["dialogues"][0]["t"] = "0.6-2.6"
        self.ecrire()
        res, _ = self.verifier()
        self.assertEqual(niveaux(res, "premiere_replique_tot"), ["À VOIR"])
        self.assertEqual(self.echecs(res), [])


# ---------------------------------------------------------------- grille narrative et Script Doctor
class Narratif(BaseProjet):
    def b(self):
        return bible.Bible(self.SOURCE)

    def test_indices_couvrent_les_11_criteres(self):
        ind = doctor.indices(self.b(), self.ep)
        self.assertEqual(set(ind), set(doctor.controles()["grille_narrative"]["criteres"]))
        for note, _ in ind.values():
            self.assertIn(note, doctor.NOTES + (None,))

    def test_hook_vide_est_un_probleme(self):
        self.ep["plans"][0]["dialogues"] = []
        self.assertEqual(doctor.indices(self.b(), self.ep)["hook"][0], "probleme")
        types = {f["type"] for f in doctor.faiblesses_auto(self.b(), self.ep)}
        self.assertIn("hook_faible", types)

    def test_retournement_sans_revelation(self):
        p = next(x for x in self.ep["plans"] if x.get("role") == "retournement")
        for d in p["dialogues"]:
            d["fonction"] = "reaction"
        types = {(f["type"], tuple(f["plans"])) for f in doctor.faiblesses_auto(self.b(), self.ep)}
        self.assertIn(("retournement_sans_consequence", (p["n"],)), types)

    def test_dialogue_explicatif_et_risque_grok(self):
        self.ep["plans"][2]["dialogues"][0]["texte"] = "Comme tu le sais, je suis ton frère"
        self.ep["plans"][3]["timeline"][0]["action"] = "une bagarre éclate entre eux"
        types = {f["type"] for f in doctor.faiblesses_auto(self.b(), self.ep)}
        self.assertIn("dialogue_explicatif", types)
        self.assertIn("trop_complexe_grok", types)

    def test_sans_revue_verdict_non_evalue(self):
        self.ecrire()
        res, ctx = self.verifier()
        d = verifier.decision(res, ctx, "ep001")
        self.assertIsNone(d["verdict"])

    def test_techniquement_valide_mais_editorialement_faible(self):
        r = self.revue_complete()
        r["grille"]["fin"] = {"note": "probleme", "constat": "la chute plan 12 est devinée dès le plan 4",
                              "correction": "plan 4 : retirer l'indice « ma femme » ; garder la révélation pour le plan 12"}
        (self.f_ep.parent / "revue.json").write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        res, ctx = self.verifier()
        d = verifier.decision(res, ctx, "ep001")
        self.assertEqual(d["bloquants"], [])
        self.assertEqual(d["verdict"], "faible")           # la grille l'emporte sur le « solide » déclaré
        with contextlib.redirect_stdout(io.StringIO()) as out:
            verifier.afficher(res, d, ctx, "ep001")
        self.assertIn("VERDICT TECHNIQUE : VALIDE", out.getvalue())
        self.assertIn("FAIBLE", out.getvalue())
        self.assertIn("la grille l'emporte", out.getvalue())

    def test_verdicts_solide_et_correct(self):
        r = self.revue_complete()
        self.assertEqual(doctor.verdict(r), "solide")
        for k in ("hook", "conflit", "fin"):
            r["grille"][k] = {"note": "a_ameliorer", "constat": "x", "correction": "y"}
        self.assertEqual(doctor.verdict(r), "correct")
        r["faiblesses"] = [{"type": "scene_inutile", "gravite": "probleme", "plans": [6], "constat": "x", "correction": "couper"}]
        self.assertEqual(doctor.verdict(r), "faible")

    def test_revue_incomplete_refusee(self):
        r = self.revue_complete()
        r["grille"]["hook"] = {"note": "a_ameliorer", "constat": "trop lent", "correction": ""}
        r["grille"].pop("climax")
        r["faiblesses"] = [{"type": "nimporte", "gravite": "grave", "correction": ""}]
        (self.f_ep.parent / "revue.json").write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        _, err, _ = doctor.lire_revue(self.b(), "ep001", self.ep)
        texte = " ".join(err)
        for attendu in ("grille.hook", "grille.climax", "type inconnu", "gravité", "pas de correction"):
            self.assertIn(attendu, texte)

    def test_revue_perimee_apres_modification(self):
        (self.f_ep.parent / "revue.json").write_text(json.dumps(self.revue_complete(), ensure_ascii=False), encoding="utf-8")
        self.assertFalse(doctor.lire_revue(self.b(), "ep001", self.ep)[2])
        self.ep["plans"][0]["dialogues"][0]["texte"] = "Autre hook."
        self.assertTrue(doctor.lire_revue(self.b(), "ep001", self.ep)[2])

    def test_code_de_sortie_ignore_le_verdict_editorial(self):
        r = self.revue_complete(verdict="faible")
        r["grille"]["hook"] = {"note": "probleme", "constat": "x", "correction": "y"}
        (self.f_ep.parent / "revue.json").write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        argv = sys.argv
        sys.argv = ["verifier.py", self.SOURCE, "ep001"]
        try:
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as fin:
                verifier.main()
        finally:
            sys.argv = argv
        self.assertEqual(fin.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
