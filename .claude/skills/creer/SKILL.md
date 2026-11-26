---
name: creer
description: Crée une vidéo IA de zéro dans le studio (studio-animaux) : vidéo unique complète OU nouvelle série, en trois validations. A) 8 à 10 concepts aux moteurs narratifs différents, tirés de toutes les analyses (mécaniques documentées, associations, angles peu exploités), avec preuves, score éditorial et faisabilité ; B) l'histoire complète (1 ou 2 variantes) ; C) personnages, décors, plans, dialogues et prompts ChatGPT (images) + Grok (vidéo). Use when the user runs /creer, asks to create a new video, a new series, or "une vidéo de zéro".
---

# /creer [idée ou thème facultatif]

Studio : racine de ce dépôt. Chaque création part de ZÉRO : nouveau dossier `projets/<id>/`, aucun personnage ni décor repris d'un autre projet.

**Trois étapes, trois validations. Ne jamais enchaîner A → B ou B → C sans la réponse de l'utilisateur.**

Principes (lire avant tout) :
- Les analyses informent, elles n'obligent pas. Une mécanique s'utilise quand elle sert l'histoire. Aucune n'est une cause démontrée de vues (pas de test A/B) : dire « associée à », « présente chez », jamais « fait des vues ».
- Ne jamais inventer une preuve. Les références affichées sont produites par `outils/creer.py` à partir des données ; une idée sans preuve s'écrit `{"hypothese": "…"}` et s'annonce comme telle.
- Les concepts diffèrent par leur **moteur narratif** (ce qui fait avancer l'histoire et la question que se pose le spectateur), pas par le décor ou l'espèce.
- Faux pauvre, test amoureux, humiliation-revanche : **saturés** (décision utilisateur). Deux concepts au plus par proposition, et seulement avec un angle neuf.

## Étape 0 · Unique ou série ?
Si l'utilisateur ne l'a pas dit : `AskUserQuestion` (Vidéo unique : histoire complète ~70 s / Nouvelle série : épisode 1 + plan de saison).

## Étape A · Concepts (attendre le choix)

### A1. Lire la connaissance (obligatoire, dans cet ordre)
1. `python3 outils/creer.py dossier` puis lire **en entier** `bible/dossier_editorial.md` : mécaniques par rubrique (socle, à tester, dépend du contexte) avec conditions et décisions des contradictions ; associations éprouvées, rares et jamais observées ; comparaisons forte/faible dans un même compte (les vidéos moins vues comptent) ; moteurs narratifs saturés ou peu exploités ; domaines rares ; greffes inutilisées ; limites.
2. `bible/editorial.json` : moteurs narratifs, émotions, grilles de score et de faisabilité, `capacites_generation`.
3. `bible/histoires.json` (squelettes et greffes) ; pour les 3-4 squelettes ou vidéos qui inspirent un concept, lire `analyses/<id>/fiche.md` (et `transcript.json` si besoin de sentir le rythme). Inclure au moins une vidéo **sous la médiane de son compte** dans la réflexion (section 3 du dossier) : qu'est-ce qui lui manquait ?
4. `bible/mecaniques.json` : pour chaque mécanique envisagée, `effet`, `fonctionnement`, `conditions`, `erreurs`. Une mécanique « dépend du contexte » n'est utilisée que si l'histoire remplit ses conditions (ex. `epreuve_verdict` adossée à une identité révélée ou une force cachée).
5. `bible/concepts.json` (`regles_generiques` : prénoms, univers inventé), `bible/conformite.json`.
6. Nos propres résultats, s'ils existent : le dernier `suivi/rapports/*.md` et le bloc `resultats_propres` des mécaniques. Ils pèsent comme le reste : une hypothèse (1 vidéo, moins de 3 projets) peut inspirer un concept « à tester », jamais l'imposer ni en écarter un. Citer le niveau de confiance quand on s'en sert.

### A2. Fabriquer les concepts EN INTERNE
Partir des moteurs narratifs, pas des personnages. Viser un mélange :
- 2-3 concepts sur des **combinaisons éprouvées** (paires « éprouvée » du dossier) mais avec un moteur non saturé ;
- 3-4 **associations nouvelles** de mécaniques connues (paires « rare » ou « jamais observées », justifiées par ce que chaque mécanique fait) ;
- 1-3 **hypothèses créatives** (moteur jamais observé, domaine candidat, mécanique à tester) : assumées comme tests.

Contraintes : 8 à 10 concepts ; moteurs narratifs tous différents ; 2 moteurs saturés au plus ; 4 émotions dominantes différentes au moins ; 5 domaines au moins (sauf thème imposé) ; le foot n'est jamais le défaut ; le thème de l'utilisateur, s'il y en a un, est respecté par tous. Éviter le moteur des 3 derniers projets.

Écrire `propositions/AAAA-MM-JJ-<slug-du-theme-ou-libre>.json` :
```json
{"date": "AAAA-MM-JJ", "type": "unique|serie", "theme": null,
 "concepts": [{
   "id": "c1", "titre": "…", "pitch": "1-2 phrases", "hook": "réplique ou image exacte de la 1re seconde",
   "conflit": "…", "emotion": "une valeur de editorial.json emotions", "curiosite": "la question qu'on veut voir tranchée",
   "retournement": "…", "fin": "…", "debat": "la question qui divise les commentaires",
   "moteur_narratif": "id de editorial.json", "domaine": "code de domaine (editorial.json domaines)",
   "mecaniques": [{"id": "ironie_dramatique", "role": "ce qu'elle fait ICI"}, {"hypothese": "nom court", "role": "…"}],
   "histoires": ["squelette ou greffe de histoires.json qui inspire (facultatif)"],
   "pourquoi_combinaison": "pourquoi ces mécaniques ensemble servent CE moteur",
   "score": {"hook": 0, "curiosite": 0, "emotion": 0, "originalite": 0, "discussion": 0, "visuel": 0},
   "justif_score": "une ligne",
   "faisabilite": {"comprehension": 1, "actions": 1, "compat_generation": 1, "nb_personnages": 4, "nb_decors": 3,
                   "risques": ["ce que l'IA risque de rater"]}}]}
```
- `refs` (facultatif) dans une mécanique = ids de vidéos d'`analyses/` ; l'outil refuse toute vidéo qui n'est pas codée avec cette mécanique. Sans `refs`, l'outil choisit lui-même les références dans les données.
- Score éditorial (/100 : hook 20, curiosité 20, émotion 20, originalité 15, discussion 15, visuel 10) : comparer les concepts entre eux, honnêtement ; 90+ doit être rare. Ce n'est pas une prédiction de vues.
- Faisabilité : `compat_generation` se juge sur `capacites_generation` (combat, foule, transformation, plus de 3 personnages qui parlent ensemble = difficile).

### A3. Contrôler et montrer
`python3 outils/creer.py concepts propositions/<fichier>.json` → corriger chaque ÉCHEC et relancer jusqu'à 0. Lire les À VOIR. L'outil calcule total, faisabilité, statut de preuve (combinaison déjà observée / association nouvelle / hypothèse), références, recommandation (meilleur score parmi les faisabilités ≥ 60), et écrit le `.md` à côté.

Montrer dans la réponse le contenu du `.md` (tableau puis une fiche par concept : titre, pitch, hook, conflit, émotion, curiosité, retournement, fin, débat, mécaniques avec statut et références, pourquoi la combinaison, score détaillé, faisabilité). Dire en une ligne la recommandation et, s'il diffère, le concept le plus ambitieux et pourquoi il n'est pas recommandé d'office.
Puis `AskUserQuestion` : les 4 concepts les mieux classés en options (le recommandé en premier), « Other » pour un autre numéro ou un mélange. **Fin de l'étape A : attendre.**

## Étape B · Histoire complète (attendre la validation)
1. `<id>` = slug court du titre (s'il existe, ajouter `-2`). Créer `projets/<id>/projet.json` :
   `{id, type, titre, sujet, concept, moteur_narratif, domaine, creer: 3, etape: "histoire", proposition: {fichier, id}, mecaniques_prevues: [...], cree}`.
2. Écrire `projets/<id>/histoire.json` :
```json
{"titre": "…", "moteur_narratif": "…", "concept": {"fichier": "propositions/….json", "id": "c4"},
 "variantes": [{"id": "A", "nom": "…", "logline": "1 phrase",
   "debut": "…", "conflit": "…",
   "motivations": [{"perso": "rôle (animal)", "veut": "…", "cache": "facultatif"}],
   "progression": ["étape 1", "…"], "retournements": ["…"], "climax": "…", "fin": "…",
   "emotions": ["0-10 s : curiosité", "…"], "personnages": ["…"], "decors": ["…"],
   "difference": "ce qui change vraiment par rapport à l'autre variante"}],
 "choix": null, "valide": null, "notes_utilisateur": ""}
```
   - Deux variantes seulement si elles diffèrent **réellement** (autre retournement, autre fin, autre camp pour le spectateur), pas une variation de détail. Sinon une seule.
   - Motivations crédibles pour chaque personnage important, y compris l'antagoniste (pourquoi il agit, de son point de vue).
   - Série : ajouter `saison` (enjeu, 8-12 pitchs d'épisodes aux formats différents, 2 secrets cachés).
3. `python3 outils/creer.py histoire <id>` → 0 ÉCHEC. Montrer le `.md` produit. `AskUserQuestion` : « Variante A / Variante B / Modifier » (ou « Valider / Modifier » si une seule). **Fin de l'étape B : attendre.**
4. Réponse reçue : écrire `choix`, `valide` (date) et `notes_utilisateur` (les retouches demandées) dans `histoire.json`, appliquer les retouches, `etape: "production"` dans `projet.json`. Une modification importante = remontrer l'histoire avant l'étape C.

## Étape C · Production (seulement après validation)
L'histoire validée est la référence : on ne change pas la fin, les retournements ni les motivations sans le dire.

**Fichiers du projet** (formats inchangés) :
- `personnages.json` (modèle `projets/faux-joueur-district/personnages.json`) : `style` = animation 3D cartoon stylisée (jamais photoréaliste) : animaux anthropomorphes aux proportions cartoon, grands yeux expressifs, expressions exagérées, couleurs saturées, décors riches pleins de figurants. 3 à 6 personnages : `id, nom, animal, adn, tenues{base,…}, voix, caractere, objectif, secret, tics[3], replique_fetiche, ref: "refs/<id>.png"`. `adn` = phrase visuelle unique et très distincte, recopiée mot pour mot dans les prompts. Prénoms : règle PRÉNOMS de `concepts.json` (majorité de prénoms français classiques adaptés à l'âge, un prénom d'origine étrangère au plus, jamais deux initiales identiques).
- `lieux.json` : `{id, nom, desc, son}`. `ton.md` : 10 lignes max (ton, humour, insultes maison, zéro mot rouge).
- Série : `saison.json` (modèle `projets/la-ferme/saison.json`).

**`episodes/ep001/episode.json`** : format exact de `projets/faux-joueur-district/episodes/ep001/episode.json` (plans `{n, role, duree: 6|10, lieu, lumiere, cadrage, angle, camera, persos[{id, tenue?, jeu}], detail_image?, texte_decor?, fin? (obligatoire pour 10 s), timeline[{t, action, camera?, son?}], dialogues[{t, parle, emotion, fonction, texte}], son?, texte_ecran?}`), plus :
- `moteur` : `desir, conflit, antagoniste` (ou obstacle), `enjeu, payoff` obligatoires ; `force_cachee, callback, kicker` seulement s'ils servent l'histoire.
- `mecaniques_utilisees` : ids de `bible/mecaniques.json` réellement utilisés (ceux de l'étape A) ; une mécanique « à tester » est assumée comme test. Sans ce champ, la vidéo publiée ne pourra pas être comparée par mécanique (`/suivi`).
- Hook : plan 1 serré, `texte_accroche` (7 mots max), 3 `hooks_alternatifs`. Plan 1 muet possible si l'image est le hook (`muet: "pourquoi"`).
- Publication : `titre_couverture`, `legende`, 4 à 7 `hashtags`, `commentaire_epingle` (vraie question d'opinion), `vote_question`. `question_milieu` si elle sert.
- `"controle": 2` (épisode soumis aux règles actuelles : moteur et fonctions obligatoires). `choix_creatifs` : `{"<id de bible/controles.json>": "pourquoi"}` pour chaque recommandation écartée volontairement.
- Codes uniquement de `bible/realisation.json` et du projet. Ne pas écrire les prompts : `pack.py` les assemble.

**Écriture : des outils, pas des quotas.**
- Toujours : dialogues naturels, parlés, expressifs, qui portent le conflit ; chaque réplique a une `fonction` (attaque, riposte, revelation, reaction, menace, promesse, aveu) ; débit 4,2 mots/s max ; actions simples pour Grok (`capacites_generation`) ; plans de 6 et 10 s ; variété de cadrages, caméras, angles, lumières ; style cartoon exagéré.
- Quand ça sert l'histoire, pas par défaut : témoin qui réagit, clash attaque → riposte en rafale, callback de la phrase du méchant, gros chiffre dans le décor, boucle de fin, retournement à position fixe, coupure au pire moment.
- Le dialogue reste la base. Un plan muet est permis s'il porte une tension ou une émotion précise (face-à-face, menace physique, découverte) : champ `muet` = ce qu'il porte. Pas de plan muet par paresse.
- Vidéo unique : dernier plan `role` = `fin`, `climax` ou `cliff` (payoff, chute, fin ouverte). Série : `cliff` + `#partieN`.

**Contrôle en deux temps** (registre : `bible/controles.json`) :
1. **Technique** : `python3 outils/verifier.py <id>` → 0 erreur bloquante (JSON, champs, codes, personnages et lieux, durées, image de fin, timecodes, débit, moteur, fonctions, conformité TikTok, assemblage réel des prompts par pack.py). Les recommandations (`editorial`) et préférences de réalisation (`preference`) ne bloquent jamais. Une préférence non suivie ne se corrige que si la scène y gagne : **jamais de réplique de remplissage pour combler un silence, jamais de témoin, de clash ou de retournement ajouté pour un compteur** ; sinon la déclarer dans `choix_creatifs`.
2. **Éditorial · Script Doctor** : lancer un sous-agent (outil `Agent`, `general-purpose`) avec seulement : « Applique `.claude/skills/doctor/SKILL.md` à `<id>` `ep001` ». Il écrit `revue.json` (grille narrative en 11 critères, faiblesses, corrections précises) sans toucher à l'épisode. Sans outil Agent : appliquer le skill soi-même, `independant: false`.
3. **Validation finale** : montrer le rapport de `verifier.py` (verdict technique, verdict éditorial, erreurs bloquantes, améliorations, points forts, risques de production), puis `AskUserQuestion` : appliquer les corrections (toutes / lesquelles) · produire tel quel · modifier. Verdict `faible` = techniquement valide mais éditorialement à retravailler : ne pas lancer `pack.py` sans cette réponse. Corrections appliquées → nouvelle revue.

**Prompts** : `python3 outils/pack.py <id>` → `episodes/ep001/pack.html` + `pack.json` (portraits, ouverture ChatGPT, Image N début/fin → ChatGPT, Vidéo N → Grok, légende, commentaire épinglé).
- PC : ouvrir `pack.html` avec `Start-Process` et donner le chemin.
- Cloud / téléphone : afficher les prompts prêts à copier depuis `pack.json` (portraits, ouverture, puis Image N / Vidéo N, légende, commentaire épinglé), puis commit + push de la branche.

**Réponse finale (courte)** : titre · casting (nom = animal, rôle) · hook · fin · verdict éditorial · choix créatifs assumés · chemin de `pack.html`. Ensuite : `/monter <id>` (PC) ; série : `/episode <id>`.

## Reprendre en cours de route
- `propositions/*.json` sans projet : l'utilisateur répond plus tard → étape B avec le concept choisi.
- `projet.json` `etape: "histoire"` et `histoire.json` sans `choix` : remontrer l'histoire, attendre la validation.
- `etape: "production"` : étape C.
- Anciens projets (sans `creer: 3`) : même vérificateur ; leurs épisodes écrits sans `moteur` ni `fonction` reçoivent ces deux contrôles en recommandation au lieu de bloquer.
