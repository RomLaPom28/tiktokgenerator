---
name: creer
description: Crée une vidéo IA de zéro dans le studio (studio-animaux) : vidéo unique complète OU nouvelle série. On choisit ensemble le type et le sujet, puis tout est généré (casting d'animaux humanisés, décors, histoire, plans, dialogues, hook, cliffhanger) à partir des analyses virales, et les prompts ChatGPT (images) et Grok (vidéo) sortent dans une page avec boutons Copier. Use when the user runs /creer, asks to create a new video, a new series, or "une vidéo de zéro".
---

# /creer [idée ou thème facultatif]

Studio : racine de ce dépôt (commandes lancées depuis la racine).
Chaque création part de ZÉRO : nouveau dossier `projets/<id>/`, aucun personnage ni décor repris d'un autre projet.

## Étape 1 · Vidéo unique ou série ?
Si l'utilisateur ne l'a pas dit : `AskUserQuestion` avec 2 choix :
- **Vidéo unique** : histoire complète en ~70 s, hook fort, chute finale qui pousse à commenter.
- **Nouvelle série** : épisode 1 + plan de saison, fin sur cliffhanger « Partie 2 ? ».

## Étape 2 · Choisir le sujet ensemble (REMIX de ce qui a déjà marché)
On n'invente pas une histoire à partir de règles : on **remixe des histoires prouvées**.

Lire d'abord (obligatoire) :
- `bible/histoires.json` : `squelettes` (histoires à 1 M+ décomposées), `greffes` (briques transplantables), `grille_gros`.
- Pour les 2-3 squelettes envisagés : leur `analyses/<id>/transcript.json` (le vrai déroulé, pour sentir le rythme et la cruauté du méchant).
- `bible/recettes.md`, `bible/concepts.json` (`regles_generiques` : prénoms, univers inventé), `bible/conformite.json`.
- `bible/mecaniques.json` : mécaniques consolidées avec confiance et signal (`preuves`). Privilégier celles de confiance élevée ; ne jamais présenter une mécanique comme « ce qui fait les vues » (corrélation seulement).
- `projets/*/projet.json` : les univers déjà faits (ne pas refaire le même domaine que l'un des 3 derniers).

**2a · Fabriquer 12 pitchs EN INTERNE (non montrés).** Chaque pitch =
`squelette` (1, de la banque) + `greffes` (1 ou 2, d'AUTRES vidéos) + **nouveau domaine** (`grille_gros.domaines_universels`) + casting d'animaux.
- Garder le moteur du squelette (secret, faute du méchant, scène attendue) ; changer l'univers, les personnages, l'objet, le chiffre.
- Pousser chaque curseur au MAX : la faute du méchant doit être grave (trahir, voler la place, enfermer, empoisonner, faire chanter), l'enjeu vital (amour, enfant, mariage, héritage à 6 chiffres+), l'image absurde.
- Le foot est un domaine parmi d'autres, jamais le défaut. Au moins 8 des 12 pitchs hors sport.
- Le thème donné par l'utilisateur, s'il y en a un, est respecté par les 12.

**2b · Noter chaque pitch avec `grille_gros`** (6 critères, 1 point chacun). Jeter tout pitch < 5/6 ou qui rate un critère éliminatoire (image_choc, enjeu_vital, faute_grave) ou qui tombe dans `interdits_pitch`. S'il en reste moins de 4, refaire des pitchs.

**2c · Montrer les 4 meilleurs**, de 4 squelettes différents, chacun sous cette forme :
```
**Titre** (note /6)
Pitch : 1 phrase « [héros] [secret/situation], mais [méchant] [faute grave] ; [enjeu chiffré]. »
Image choc (1 s, sans le son) : …
Hook : « 1re réplique exacte »
La scène qu'on attend : …
Retournement : …
Fin : payoff + kicker (ou cliffhanger)
Remix : squelette <id> (X M) + greffe <id> (source Y M)
```
Recommander un des 4 (le plus haut, à égalité celui dont les sources ont le plus de vues). Puis `AskUserQuestion` (4 sujets ; « Other » permet d'en donner un autre ou d'en mixer deux).
**C'est la seule validation.** Ensuite tout est généré d'une traite. Noter dans `projet.json` le champ `remix: {squelette, greffes[], note}`.

## Étape 3 · Générer le projet `projets/<id>/`
`<id>` = slug court du titre (minuscules, tirets). S'il existe déjà, ajouter `-2`.

**`projet.json`** : `{id, type: "unique"|"serie", titre, sujet, concept, cree: "AAAA-MM-JJ"}`.

**`personnages.json`** (modèle : `projets/la-ferme/personnages.json`) :
- `style` : ANIMATION 3D CARTOON STYLISÉE (pas photoréaliste) façon long-métrage d'animation premium : animaux anthropomorphes aux proportions cartoon (tête un peu grosse, grands yeux expressifs, sourcils très mobiles), expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés, couleurs saturées et chaudes, lumière dorée/contre-jour dramatique, décors riches pleins de figurants animaux. Adapter l'univers au sujet (stade, vestiaire, villa…). Exemple validé par l'utilisateur : `projets/faux-joueur-district/personnages.json`.
- 3 à 6 personnages. Chacun : `id, nom, animal, adn, tenues{base, + autres si besoin}, voix, caractere, objectif, secret, tics[3], replique_fetiche, ref: "refs/<id>.png"`.
- `adn` = phrase visuelle unique et TRÈS distincte (espèce, couleur dominante, signe particulier, accessoire signature), recopiée mot pour mot dans les prompts : rien d'autre ne décrit le personnage.
- Prénoms français courants adaptés à l'âge (règle PRÉNOMS de `concepts.json`) : majorité de prénoms français classiques (Lucas, Hugo, Chloé, Manon, Sandrine…), AU MAXIMUM un prénom d'origine maghrébine/étrangère par casting. Jamais un casting entier du même registre. Espèce choisie pour le look et le caractère.

**`lieux.json`** : 3 à 6 lieux `{id, nom, desc, son}` (desc = phrase visuelle précise, son = ambiance).

**`ton.md`** : 10 lignes max : le ton, ce qui est drôle, insultes maison propres au sujet (zéro mot rouge).

**Série seulement, `saison.json`** (modèle : `projets/la-ferme/saison.json`) : `enjeu`, 8 à 12 `episodes[{n, format, pitch}]` (formats tous différents, valeurs de `realisation.json`), `fils[{id, statut: ouvert|cache, texte}]` (2 secrets cachés minimum).

## Étape 4 · Écrire `projets/<id>/episodes/ep001/episode.json`
Modèle EXACT du nouveau format : `projets/faux-joueur-district/episodes/ep001/episode.json`. Lire aussi la section « Machine virale v2 » de `bible/recettes.md`.

**Chaque plan** :
```
{n, role: accroche|developpement|retournement|temoin|climax|cliff, duree: 6|10, lieu, lumiere, cadrage, angle, camera,
 persos:[{id, tenue?, jeu}],            // = IMAGE DE DÉBUT
 detail_image?, texte_decor?,           // texte_decor = texte lisible DANS le décor (tableau d'affichage, banderole, chiffre géant)
 fin?: {cadrage?, angle?, persos:[{id, jeu}], detail_image?},   // OBLIGATOIRE si duree 10 = IMAGE DE FIN
 timeline:[{t:"0-2", action, camera?, son?}],                   // un temps fort toutes les 3 s max
 dialogues:[{t:"0.3-1.8", parle, emotion, texte}],              // timecodes en secondes, 4,2 mots/s max
 son?, texte_ecran?}                                             // texte_ecran = gros mot affiché au montage
```
**Avant les plans, écrire `moteur`** (section « Moteur d'histoire » de `recettes.md`, OBLIGATOIRE) :
`{desir, injustice, antagoniste, enjeu_chiffre, force_cachee, payoff, callback, kicker}` — `callback` = phrase-signature EXACTE du méchant, dite une 1re fois par lui et renvoyée contre lui au payoff.
Tester l'histoire en 4 phrases : « On aime X parce que… Y l'humilie injustement en… On attend que… Ça paie quand… ». Si une phrase est faible, changer l'histoire avant d'écrire.
Chaque dialogue a `fonction` : attaque | riposte | revelation | reaction | menace | promesse | aveu (jamais info). 4+ clashs attaque → riposte. Parole sur 55 %+ de chaque plan, jamais 1,5 s de silence.

Règles d'écriture (HYPER DYNAMIQUE) :
- **12 à 16 plans**, mélange de 6 s (punch) et 10 s (scènes clés), au moins 2 × 10 s et 4 × 6 s, rush total 68-92 s.
- **Rupture toutes les 2-3 s** : action → réplique → réaction → coup de caméra (`whip_pan`, `crash_zoom`, `ralenti`, `secousse`…) → bruitage.
- **Ping-pong** : 4+ plans où 2 personnages se répondent ; répliques de 1 à 12 mots, parlées, françaises, qui claquent ; un **témoin** qui réagit en 1 mot (« QUOI ?! ») après chaque réplique-choc.
- **Hook (plan 1)** : 1re réplique à 0-0,5 s, dit le drame/le secret, cadrage serré. `texte_accroche` 7 mots max. `hooks_alternatifs` : 3 autres premières répliques possibles.
- **Plan 2** : contexte en une phrase. **Retournements** plans 3-6 ET 7-11. **`question_milieu`** {plan 5-8, texte}.
- **Dernier plan** `role: "cliff"` : série = coupé au pire moment + `#partieN` ; vidéo unique = `twist final` / `fin ouverte au vote` / `boucle` (la dernière réplique doit pouvoir s'enchaîner avec la première → revisionnages).
- **Gros chiffre / texte lisible** dans au moins un `texte_decor` (score, prix, « 80 M€ »), noms 100 % fictifs.
- **Varier** : jamais 2 cadrages identiques d'affilée, 5 cadrages et 4 caméras min, 3 angles, 3 lieux (sauf huis clos), 2 lumières.
- **Jeu** : expressions cartoon EXAGÉRÉES (yeux exorbités, mâchoire qui tombe, oreilles qui se plaquent), tics de la fiche, au moins un contraste comique.
- Actions Grok simples et lisibles (pointer, se lever d'un bond, claquer, lancer un objet, s'effondrer à genoux) : l'histoire passe par les dialogues.
- `recettes_utilisees` : au moins 3 recettes de `recettes.md`.
- Publication : `titre_couverture`, `legende`, 4 à 7 `hashtags`, `commentaire_epingle` = question binaire avec 2 émojis et un « / », `vote_question`.
- Codes (`lieu, lumiere, cadrage, angle, camera, format, accroche_type, cliff_type`) : uniquement des valeurs de `bible/realisation.json` et du projet. Ne PAS écrire les prompts : `pack.py` les assemble.

## Étape 5 · Contrôle qualité
`python outils/verifier.py <id>` (ou `<id> ep001`) → corriger chaque ÉCHEC, relancer jusqu'à 0. Relire les « À VOIR ».
Relire soi-même : le hook arrête-t-il le pouce en 1 s ? Chaque réplique sonne-t-elle parlée ? La fin donne-t-elle envie de commenter ? Sinon, réécrire.

## Étape 6 · Prompts
`python outils/pack.py <id>` → `projets/<id>/episodes/ep001/pack.html` (et `pack.json`) :
0. Portraits de référence → ChatGPT (une fois par personnage, à enregistrer dans `projets/<id>/refs/`)
1. Message d'ouverture → nouvelle conversation ChatGPT (+ portraits joints)
2. Pour chaque plan : « Image N début » (+ « Image N fin » pour les 10 s) → ChatGPT, puis dans Grok : image(s) + « Vidéo N », durée réglée sur 6 ou 10 s
3. Légende + hashtags, commentaire épinglé
Ouvrir la page : `start "" "projets/<id>/episodes/ep001/pack.html"` (PowerShell : `Start-Process`).

## Étape 7 · Répondre (court)
Titre · casting en une ligne (nom = animal, rôle) · hook · fin. Ouvrir `pack.html` dans le navigateur de l'utilisateur avec `Start-Process` (les prompts y sont affichés en clair avec boutons Copier) et donner le chemin complet.
Ensuite : clips Grok dans Téléchargements → `/monter <id>` ; série → épisode suivant avec `/episode <id>`.
