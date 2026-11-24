# Studio : mode d'emploi

## Copier une vidéo qui a percé (le plus rapide)
1. **`/copier <lien TikTok>`** (ou l'id d'une vidéo déjà dans `analyses/`).
2. L'outil découpe tout : plans, personnages (combien, qui, look), décors, transcription attribuée à chaque perso.
3. Il explique pourquoi la vidéo marche, ses faiblesses, et ce qu'on peut améliorer pour la viralité.
   Tout est écrit dans `analyses/<id>/dissection.md` (avec un brief collable dans `/creer`).
4. Il propose 3 transpositions (nouvel univers, nouveaux animaux). Tu en choisis une.
5. Il réécrit l'histoire réplique par réplique (même rôle, même place, autres mots) et sort `pack.html` :
   en haut, le tableau **Original → notre version**, puis tous les prompts ChatGPT + Grok.
   Le contrôle qualité refuse toute réplique trop proche de l'original et tout nom propre repris.
   Vidéo source de plus de 95 s : découpée en parties (série), la suite avec `/episode <id>`.

## Créer une vidéo (toujours de zéro)
1. **`/creer`** (ou `/creer` + un thème, ex. `/creer foot`).
2. Tu choisis : **vidéo unique** ou **nouvelle série**.
3. **Étape A** : Claude lit le dossier éditorial (toutes les analyses : mécaniques documentées, à tester, associations, vidéos fortes et faibles d'un même compte, formats saturés, angles peu exploités) et propose **8 à 10 concepts** aux moteurs narratifs différents. Chacun : titre, pitch, hook, conflit, émotion, curiosité, retournement, fin, débat, mécaniques avec leurs références d'analyses (jamais inventées), statut (observé / association nouvelle / hypothèse), score éditorial /100 et faisabilité /100. Tu choisis.
4. **Étape B** : l'histoire complète (début, conflit, motivations, progression, retournements, climax, fin), en 1 ou 2 variantes vraiment différentes. Tu valides ou tu modifies.
5. **Étape C** : personnages, décors, plans, dialogues, hook, fin, publication. Contrôle qualité (codes, durées, conformité TikTok bloquants ; techniques de rythme signalées en « À VOIR », jamais imposées).
6. Une page `pack.html` s'ouvre avec des boutons Copier :
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
- `bible/` : commun à tous les projets : `editorial.json` (moteurs narratifs, grilles de score et de faisabilité, capacités de génération), `dossier_editorial.md` (généré par `python3 outils/creer.py dossier`), `histoires.json` (banque d'histoires à 1 M+ où /creer puise), `recettes.md` + `concepts.json` (analyses), `mecaniques.json` (bibliothèque des mécaniques : catégorie, effet, fonctionnement, conditions, erreurs, niveau à tester / récurrente / fortement documentée, sources, contradictions ; `python3 outils/mecaniques.py` recalcule les preuves, `analyses/MECANIQUES.md` et la section générée de `recettes.md`), `conformite.json` (règles TikTok),
  `realisation.json` (cadrages, caméras, lumières, types d'accroche et de fin).
- `analyses/`, `sources/` : vidéos TikTok analysées. `outils/` : scripts. `musique/` : mp3 libres de droits.

## Commandes manuelles
- `python outils/verifier.py <id> [epNNN]` : contrôle qualité.
- `python outils/pack.py <id> [epNNN]` : régénère les prompts.
- `python3 outils/creer.py dossier` : recalcule le dossier éditorial ; `concepts propositions/<fichier>.json` : contrôle des concepts (étape A) ; `histoire <id>` : contrôle de l'histoire (étape B).
- `propositions/` : les lots de concepts proposés par /creer (`.json` + `.md` lisible), gardés pour y revenir plus tard.
