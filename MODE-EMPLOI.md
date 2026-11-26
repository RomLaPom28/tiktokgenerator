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
5. **Étape C** : personnages, décors, plans, dialogues, hook, fin, publication. Contrôle qualité en deux verdicts :
   - **technique** (bloquant) : fichiers lisibles, personnages et décors connus, timecodes, durées 6/10 s, débit, conformité TikTok, prompts assemblables ;
   - **éditorial** : le **Script Doctor** relit l'épisode sans avoir participé à l'écriture, note 11 critères (hook, raison de rester, désir, conflit, enjeux, motivations, retournements, dialogues, scènes visuelles, climax, fin) et propose des corrections précises. Tu choisis : corriger, produire tel quel, modifier.
   Le rapport affiche : erreurs bloquantes, améliorations recommandées, points forts, risques de production, verdict éditorial. Les préférences de rythme (silences, ping-pong, nombre de retournements…) sont signalées, jamais imposées.
6. Une page `pack.html` s'ouvre avec des boutons Copier :
   - **0. Portraits** → ChatGPT, une fois par personnage (enregistre-les dans `projets/<id>/refs/`).
   - **1. Ouverture** → nouvelle conversation ChatGPT, portraits joints.
   - **Image N → ChatGPT**, puis dans Grok : l'image + **Vidéo N → Grok**.
   - **Légende + hashtags**, **commentaire épinglé**.

## Ensuite
- **`/monter <id>`** : monte les clips Grok (pris dans Téléchargements) en vidéo finale 9:16 sous-titrée.
- **`/suivi`** : après publication, donne les chiffres de TikTok Studio (voir « Suivre les performances »).
- **`/episode <id>`** : épisode suivant d'une série (reprend la fin du précédent).
- **`/analyser`** + liens TikTok : apprend des vidéos virales. Ça nourrit tous les futurs `/creer`.

## Suivre les performances de tes vidéos
1. **Relever** dans TikTok Studio → Analyse de la vidéo, de préférence à **J+2** et **J+7** (J+30 si elle vit encore) : vues, likes, commentaires, partages, favoris, temps moyen de visionnage, taux de complétion (« a regardé la vidéo en entier »), nouveaux abonnés, revenus. Ce que tu n'as pas : laisse vide, rien n'est estimé.
2. **Saisir**, au choix :
   - dans le chat (PC ou téléphone) : `/suivi prodige-34-ans publiée le 20/11, relevé du 27/11 : 12 400 vues, 830 likes, 95 commentaires, complétion 41 %` ;
   - dans Excel : `suivi/stats.csv`, une ligne par relevé (séparateur « ; », dates AAAA-MM-JJ ou JJ/MM/AAAA), puis `python outils/suivi.py verifier` ;
   - en commande : `python outils/suivi.py ajouter prodige-34-ans --publie 2026-11-20 --releve 2026-11-27 --vues 12400 --likes 830 --commentaires 95 --completion 41`.
   Le concept, le moteur, les mécaniques, le hook, la fin et le format sont lus dans le projet : rien à ressaisir. Pour comparer par mécanique, l'épisode doit avoir `mecaniques_utilisees` (`/suivi` le propose et te le fait valider).
3. **Rapport** (toutes les 2 à 4 semaines) : `/suivi rapport` ou `python outils/suivi.py rapport [--age 7]` → `suivi/rapports/AAAA-MM-JJ.md` : ce qui marche le mieux, moins bien, hypothèses, mécaniques à réutiliser, à retravailler, prochaines expériences.
   Lecture : « ×1,8 » = 1,8 fois la médiane des autres vidéos au même âge. « Hypothèse » = 1 vidéo ou moins de 3 projets. « Signal répété » = 3 projets concordants sans variable confondue. Ce n'est jamais une preuve de cause.
4. **Test A/B** (le seul qui approche une cause) : même épisode republié avec un autre hook (`hooks_alternatifs`), colonnes `test` (même nom pour les deux) et `variante` (A, B), relevés à J+2.
5. Comparer deux vidéos : `python outils/suivi.py liste` puis `python outils/suivi.py comparer <pubA> <pubB>`.

## Dossiers
- `projets/<id>/` : un projet = une vidéo unique ou une série (personnages, décors, saison, épisodes, prompts, vidéo finale).
  `projets/la-ferme/` = la 1re série (Gérard, Vanessa…), avec sa page téléphone (`/studio`).
- `bible/` : commun à tous les projets : `editorial.json` (moteurs narratifs, grilles de score et de faisabilité, capacités de génération), `dossier_editorial.md` (généré par `python3 outils/creer.py dossier`), `histoires.json` (banque d'histoires à 1 M+ où /creer puise), `recettes.md` + `concepts.json` (analyses), `mecaniques.json` (bibliothèque des mécaniques : catégorie, effet, fonctionnement, conditions, erreurs, niveau à tester / récurrente / fortement documentée, sources, contradictions ; `python3 outils/mecaniques.py` recalcule les preuves, `analyses/MECANIQUES.md` et la section générée de `recettes.md`), `conformite.json` (règles TikTok),
  `realisation.json` (cadrages, caméras, lumières, types d'accroche et de fin).
- `analyses/`, `sources/` : vidéos TikTok analysées. `outils/` : scripts. `musique/` : mp3 libres de droits.

## Commandes manuelles
- `python outils/verifier.py <id> [epNNN] [--detail]` : contrôle qualité (verdict technique + verdict éditorial ; `--detail` liste chaque contrôle).
- `/doctor <id> [epNNN]` : critique éditoriale (Script Doctor) d'un épisode, même ancien. `python3 outils/doctor.py <id> [epNNN]` : ses indices automatiques seuls.
- `python3 -m unittest discover -s tests` : tests (contrôle qualité, suivi des performances ; tous les projets existants doivent rester valides).
- `suivi/stats.csv` : relevés de nos vidéos publiées ; `suivi/rapports/` : rapports de performances.
- `bible/controles.json` : liste des contrôles, leur nature (technique / editorial / preference) et leurs seuils.
- `python outils/pack.py <id> [epNNN]` : régénère les prompts.
- `python3 outils/creer.py dossier` : recalcule le dossier éditorial ; `concepts propositions/<fichier>.json` : contrôle des concepts (étape A) ; `histoire <id>` : contrôle de l'histoire (étape B).
- `propositions/` : les lots de concepts proposés par /creer (`.json` + `.md` lisible), gardés pour y revenir plus tard.
