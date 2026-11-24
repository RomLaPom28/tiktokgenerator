# Mécaniques observées — généré le 24/11/2026

> Fichier GÉNÉRÉ par `python3 outils/mecaniques.py` : ne pas éditer. Source : `analyses/*/mecaniques.json` + `bible/mecaniques.json`.

**Corpus** : 72 vidéos codées sur 72, 15 comptes, 4 codages vérifiés (fiche v2 ou dissection), 68 rétro-codés depuis les fiches v1. Médiane de compte réelle connue pour 0 compte(s) sur 15.

**Biais à garder en tête** : (1) les vidéos ont été choisies parmi les PLUS VUES de chaque compte, donc « présent dans X vidéos à 1 M+ » décrit les gagnants, pas l'effet de la mécanique ; (2) un seul genre (« fruit drama » FR, 3D, novembre 2026) : un effet « multi-univers » ne veut dire que plusieurs domaines d'histoire dans ce genre ; (3) les suites perdent des vues par construction : exclues du signal de performance.

**Lecture** : *Confiance* = récurrence (faible : 1 compte · moyen : 2-3 comptes · élevé : 4+ comptes et 4+ histoires). *Signal intra-compte* = vues médianes des vidéos AVEC la mécanique ÷ vidéos SANS, dans le même compte, hors suites ; « indéterminé » sous 2 comptes de contraste. *Robuste* = le signal garde son sens en partie 1 seule, en vidéos uniques/longues seules et hors ton noir ; *fragile* = il s'inverse dans un de ces sous-groupes (effet probable du format ou du ton, pas de la mécanique). Les deux sont des corrélations ; la causalité exige nos propres tests A/B.

## Mécaniques consolidées

| Mécanique | Type | Vidéos (vérif.) | Comptes | Histoires | Domaines | Vues méd. hors suites | Signal intra-compte | Confiance |
|---|---|---|---|---|---|---|---|---|
| **Le spectateur sait, les personnages non** `ironie_dramatique` | narrative | 30 (2) | 13 | 26 | 10 | 1,9 M | positif ×1,82 (9 cpt) · **fragile** | élevé |
| **Couper la vidéo au seuil de la révélation** `coupure_avant_payoff` | narrative | 22 (2) | 13 | 20 | 10 | 1,9 M | neutre ×1,21 (10 cpt) | élevé |
| **Injustice publique contre le héros qu'on aime** `humiliation_injuste` | narrative | 21 (2) | 13 | 20 | 10 | 1,9 M | positif ×1,94 (10 cpt) · **fragile** | élevé |
| **Le méprisé se révèle supérieur devant ceux qui l'ont méprisé** `renversement_statut` | narrative | 24 (2) | 12 | 20 | 11 | 1,0 M | positif ×1,37 (8 cpt) · **fragile** | élevé |
| **Série en parties avec reprise exacte de la fin** `suite_partie_n` | format | 20 (2) | 11 | 13 | 8 | non disponible | indéterminé | élevé |
| **Une question binaire posée tôt, tranchée à la fin** `epreuve_verdict` | narrative | 17 (2) | 10 | 15 | 7 | 1,5 M | négatif ×0,69 (6 cpt) · **fragile** | élevé |
| **Un gros chiffre lisible dans l'image** `chiffre_ecran` | realisation | 13 (1) | 9 | 12 | 8 | 1,9 M | positif ×1,35 (5 cpt) · robuste | élevé |
| **Une règle absurde du monde annoncée à 0 s** `regle_du_monde` | narrative | 11 (0) | 6 | 9 | 5 | 1,2 M | neutre ×1,56 (4 cpt) | élevé |
| **Un tiers vulnérable fait monter l'enjeu** `proche_en_danger` | narrative | 8 (0) | 5 | 6 | 2 | 1,8 M | neutre ×1,3 (4 cpt) | élevé |
| **Le héros pourrait riposter mais s'en empêche** `retenue_volontaire` | narrative | 3 (1) | 3 | 3 | 2 | 2,6 M | neutre ×1,02 (3 cpt) | moyen |
| **Tension muette, plans courts, peu de mots** `style_muet` | realisation | 8 (0) | 2 | 4 | 3 | 1,9 M | indéterminé ×18,79 (1 cpt) | moyen |

- `ironie_dramatique` : variantes : aveu_0s 8 vid./4 cpt (élevé, signal neutre ×1,07/3 cpt) · complot_montre 13 vid./8 cpt (élevé, signal neutre ×0,99/5 cpt) · identite_cachee 9 vid./7 cpt (élevé, signal positif ×2,66/4 cpt) ; signal fragile : s'inverse en partie_1 ×0,84 ; vue dans 10 domaines
- `epreuve_verdict` : variantes : test_amour 8 vid./5 cpt (élevé, signal négatif ×0,74/3 cpt) · test_honnetete 1 vid./1 cpt (faible, signal indéterminé) · concours 8 vid./6 cpt (élevé, signal neutre ×0,86/6 cpt) ; signal fragile : s'inverse en unique/long ×1,19 ; vue dans 7 domaines ; contradiction : fréquente mais sous-performe dans ses propres comptes
- `humiliation_injuste` : variantes : mepris_apparence 10 vid./6 cpt (élevé, signal neutre ×0,87/5 cpt) · mepris_argent 2 vid./2 cpt (moyen, signal neutre ×5,22/2 cpt) · accusation_a_tort 1 vid./1 cpt (faible, signal indéterminé) · chouchou_parent 2 vid./2 cpt (moyen, signal positif ×1,98/2 cpt) ; signal fragile : s'inverse en unique/long ×0,94 ; vue dans 10 domaines
- `renversement_statut` : variantes : transformation 8 vid./5 cpt (élevé, signal négatif ×0,71/4 cpt) · force_cachee 7 vid./6 cpt (élevé, signal positif ×1,95/4 cpt) · identite_revelee 6 vid./6 cpt (élevé, signal positif ×9,44/3 cpt) · callback 2 vid./2 cpt (moyen, signal indéterminé) ; signal fragile : s'inverse en unique/long ×0,77 ; vue dans 11 domaines
- `retenue_volontaire` : variantes : promesse 0 vid./0 cpt (aucune preuve, signal indéterminé) · test_en_cours 1 vid./1 cpt (faible, signal indéterminé ×1,02/1 cpt) · handicap_impose 2 vid./2 cpt (moyen, signal neutre ×2,46/2 cpt) ; concentrée sur le ton « drame » : effet du contexte possible
- `proche_en_danger` : variantes : frere_menace 5 vid./3 cpt (moyen, signal indéterminé ×0,23/1 cpt) · enfant_seul 2 vid./2 cpt (moyen, signal neutre ×1,21/2 cpt)
- `regle_du_monde` : variantes : chiffre_social 5 vid./4 cpt (élevé, signal positif ×5,95/2 cpt) · pacte 3 vid./2 cpt (moyen, signal neutre ×0,8/2 cpt) · rite 2 vid./1 cpt (faible, signal indéterminé ×0,61/1 cpt) ; vue dans 5 domaines
- `coupure_avant_payoff` : variantes : vous_voulez_voir 7 vid./6 cpt (élevé, signal neutre ×1,05/4 cpt) · menace_annoncee 7 vid./5 cpt (élevé, signal neutre ×1,22/4 cpt) · arrivee_annoncee 7 vid./7 cpt (élevé, signal positif ×2,36/5 cpt) ; concentrée sur le ton « drame » : effet du contexte possible ; vue dans 10 domaines
- `chiffre_ecran` : variantes : front 6 vid./5 cpt (élevé, signal positif ×2,45/3 cpt) · decor 7 vid./6 cpt (élevé, signal neutre ×1,03/4 cpt) ; vue dans 8 domaines
- `style_muet` : concentrée sur le ton « drame » : effet du contexte possible ; vue dans 3 domaines
- `suite_partie_n` : variantes : reprise_exacte 7 vid./7 cpt (élevé, signal indéterminé) ; concentrée sur le ton « drame » : effet du contexte possible ; vue dans 8 domaines

## Candidates (une seule source ou à confirmer)

| Mécanique | Type | Vidéos (vérif.) | Comptes | Histoires | Domaines | Vues méd. hors suites | Signal intra-compte | Confiance |
|---|---|---|---|---|---|---|---|---|
| **L'information change de camp une seconde fois** `double_retournement` | narrative | 2 (0) | 2 | 2 | 2 | 3,2 M | indéterminé ×1,68 (1 cpt) | moyen |
| **Un témoin réagit juste après la réplique-choc** `temoin_reaction` | realisation | 1 (0) | 1 | 1 | 1 | 2,9 M | indéterminé ×19,67 (1 cpt) | faible |
| **Compilation « le film » d'une série terminée** `compilation_film` | format | 1 (0) | 1 | 1 | 1 | non disponible | indéterminé | faible |

- `double_retournement` : variantes : allie_menteur 1 vid./1 cpt (faible, signal indéterminé ×1,68/1 cpt) · victime_manipulatrice 1 vid./1 cpt (faible, signal indéterminé) ; candidate vue chez 2 comptes ou plus : à promouvoir « consolidee » après relecture

## Facteurs de contexte (ton, format, domaine)

| Facteur | Vidéos | Comptes | Vues méd. | Signal intra-compte |
|---|---|---|---|---|
| ton : drame | 43 | 14 | 1,3 M | positif ×1,51 (11 cpt) · fragile (s'inverse en unique/long ×1) |
| ton : noir | 14 | 8 | 769 k | négatif ×0,54 (8 cpt) · robuste |
| ton : comique | 12 | 5 | 1,1 M | neutre ×0,98 (5 cpt) |
| ton : horreur | 2 | 2 | 2,2 M | positif ×1,86 (2 cpt) · robuste |
| ton : triste | 1 | 1 | 101 k | indéterminé ×0,66 (1 cpt) |
| format : suite | 24 | 14 | 817 k | exclu (suite/compilation) |
| format : unique | 21 | 10 | 1,0 M | négatif ×0,41 (7 cpt) |
| format : partie_1 | 18 | 11 | 1,9 M | positif ×2,05 (8 cpt) |
| format : episode_long | 8 | 3 | 671 k | neutre ×0,98 (2 cpt) |
| format : compilation | 1 | 1 | 7,0 M | exclu (suite/compilation) |
| domaine : couple | 22 | 10 | 1,6 M | positif ×1,38 (10 cpt) · fragile (s'inverse en partie_1 ×0,84, unique/long ×0,94, hors ton noir ×0,87) |
| domaine : famille | 15 | 8 | 708 k | négatif ×0,51 (8 cpt) · robuste |
| domaine : lycee | 7 | 2 | 410 k | indéterminé ×19,67 (1 cpt) |
| domaine : argent | 5 | 3 | 1,3 M | indéterminé ×1,15 (1 cpt) |
| domaine : concours | 5 | 3 | 1,2 M | négatif ×0,71 (3 cpt) · robuste |
| domaine : sport | 4 | 3 | 1,4 M | positif ×1,52 (3 cpt) · robuste |
| domaine : fantastique | 4 | 1 | 793 k | indéterminé ×0,66 (1 cpt) |
| domaine : travail | 3 | 1 | non disponible | indéterminé |
| domaine : mariage | 2 | 2 | 2,2 M | positif ×7,01 (2 cpt) · robuste |
| domaine : prison | 2 | 2 | 636 k | indéterminé ×0,92 (1 cpt) |
| domaine : belle-famille | 2 | 1 | 1,3 M | indéterminé ×0,59 (1 cpt) |
| domaine : quartier | 1 | 1 | 1,9 M | indéterminé ×12,89 (1 cpt) |

