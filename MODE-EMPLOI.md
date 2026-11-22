# Studio : mode d'emploi

## Créer une vidéo (toujours de zéro)
1. **`/creer`** (ou `/creer` + un thème, ex. `/creer foot`).
2. Tu choisis : **vidéo unique** ou **nouvelle série**.
3. Claude propose 4 sujets basés sur les analyses virales (hook + fin pour chacun). Tu en choisis un, ou tu donnes le tien.
4. Claude génère tout : personnages (animaux humanisés), décors, histoire, 12 plans, dialogues, hook, cliffhanger, publication.
   Contrôle qualité automatique (structure, rythme, rétention, règles TikTok).
5. Une page `pack.html` s'ouvre avec des boutons Copier :
   - **0. Portraits** → ChatGPT, une fois par personnage (enregistre-les dans `projets/<id>/refs/`).
   - **1. Ouverture** → nouvelle conversation ChatGPT, portraits joints.
   - **Image N → ChatGPT**, puis dans Grok : l'image + **Vidéo N → Grok**.
   - **Légende + hashtags**, **commentaire épinglé**.

## Ensuite
- **`/monter <id>`** : monte les clips Grok (pris dans Téléchargements) en vidéo finale 9:16 sous-titrée.
- **`/episode <id>`** : épisode suivant d'une série (reprend la fin du précédent).
- **`/analyser`** + liens TikTok : apprend des vidéos virales. Ça nourrit tous les futurs `/creer`.

## Dossiers
- `projets/<id>/` : un projet = une vidéo unique ou une série (personnages, décors, saison, épisodes, prompts, vidéo finale).
  `projets/la-ferme/` = la 1re série (Gérard, Vanessa…), avec sa page téléphone (`/studio`).
- `bible/` : commun à tous les projets : `recettes.md` + `concepts.json` (analyses), `conformite.json` (règles TikTok),
  `realisation.json` (cadrages, caméras, lumières, types d'accroche et de fin).
- `analyses/`, `sources/` : vidéos TikTok analysées. `outils/` : scripts. `musique/` : mp3 libres de droits.

## Commandes manuelles
- `python outils/verifier.py <id> [epNNN]` : contrôle qualité.
- `python outils/pack.py <id> [epNNN]` : régénère les prompts.
