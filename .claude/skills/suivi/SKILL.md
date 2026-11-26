---
name: suivi
description: Suivi des performances des vidéos PUBLIÉES du studio (studio-animaux) : enregistre les statistiques saisies à la main (vues, likes, commentaires, partages, favoris, temps moyen, complétion, abonnés, revenus), compare les vidéos (même âge, durée proche, hooks, fins, moteurs, mécaniques) et produit le rapport périodique (ce qui marche, ce qui marche moins, hypothèses, mécaniques à réutiliser ou à retravailler, prochaines expériences). Use when the user runs /suivi, gives stats of a published video (« prodige : 12 000 vues, 800 likes »), asks how their videos perform, or asks for the performance report.
---

# /suivi [stats en vrac | rapport | liste | comparer A B]

Données : `suivi/stats.csv` (une ligne = un relevé d'une publication à une date). Outil : `python3 outils/suivi.py`. Python seul : marche sur le PC, le cloud et depuis le téléphone. Aucune API, aucun abonnement : l'utilisateur recopie les chiffres de TikTok Studio.

## Règles (non négociables)
- **Jamais d'estimation.** Une donnée non donnée reste vide. Pas de « ~12K » converti : demander le chiffre exact de TikTok Studio, ou laisser vide. Pas de durée tirée des rushs.
- **Même âge.** Noter la date de publication ET la date du relevé. Relevés conseillés : J+2 (hook, test A/B) et J+7 (comparaison), J+30 si la vidéo vit encore.
- **Corrélation, pas cause.** Ne jamais écrire qu'une mécanique, un hook ou un concept « a fait » les vues. Toujours citer les variables confondues que donne le rapport.
- **Confiance.** 1 vidéo ou moins de 3 projets = hypothèse. « Signal répété » = 3 projets concordants sans variable confondue. Seul un test A/B (même épisode, deux variantes) approche une cause.
- **Apprentissage borné.** `suivi.py rapport` écrit seulement le bloc calculé `resultats_propres` des mécaniques. Ne jamais modifier à la main, à partir de ces résultats, `bible/controles.json`, les règles de `recettes.md`, CLAUDE.md ni les champs manuels de `bible/mecaniques.json`. Proposer à l'utilisateur ; il décide.

## 1. Saisir des stats
1. Identifier la publication : projet (`projets/*/projet.json`), épisode (ep001 par défaut), plateforme (tiktok par défaut), date de publication. Ambigu → `AskUserQuestion`.
2. Si l'épisode n'a pas `mecaniques_utilisees` : proposer la liste (ids de `bible/mecaniques.json`, d'après l'épisode réellement écrit) et la faire valider avant de l'écrire dans `episode.json`. Sans elle, la vidéo est exclue des comparaisons de mécaniques.
3. `python3 outils/suivi.py ajouter <projet> [epNNN] --publie AAAA-MM-JJ [--releve AAAA-MM-JJ] --vues N [--likes N] [--commentaires N] [--partages N] [--favoris N] [--temps-moyen S] [--completion PCT] [--abonnes N] [--revenus EUR] [--duree S]` (`--test ID --variante TXT` pour un test A/B, `--compte` si plusieurs comptes). L'outil refuse une ligne incohérente sans rien écrire.
4. Cloud / téléphone : commit + push de `suivi/` (et des `episode.json` complétés) pour que le PC récupère.
5. Répondre en une ligne : enregistré, âge du relevé, données manquantes utiles (complétion, temps moyen).

L'utilisateur peut aussi remplir `suivi/stats.csv` dans Excel (séparateur « ; », une ligne par relevé, cellule vide = inconnu) puis lancer `python3 outils/suivi.py verifier`.

## 2. Rapport
1. `python3 outils/suivi.py verifier` → corriger avec l'utilisateur toute erreur.
2. `python3 outils/suivi.py rapport [--age 7]` → `suivi/rapports/AAAA-MM-JJ.md` + `resultats_propres` dans `bible/mecaniques.json`.
3. Montrer les sections 1 à 6, telles quelles, avec les niveaux de confiance. Ajouter en 3 lignes max ce que tu en retiens, sans rien affirmer de plus fort que le rapport.
4. Si une piste mérite de changer une recette ou une règle : la proposer à l'utilisateur, ne rien modifier sans son accord.

## 3. Comparer deux vidéos
`python3 outils/suivi.py liste` puis `python3 outils/suivi.py comparer <pubA> <pubB> [--age N]` : les caractéristiques qui diffèrent sont listées ; plus d'une différence = aucune n'explique l'écart à elle seule.
