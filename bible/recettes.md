# Recettes virales

> Trois parties, sans redite :
> 1. **Bibliothèque des mécaniques** (générée) : ce que disent les analyses, avec le niveau de preuve. Observations, pas obligations.
> 2. **Règles de fabrication** : choix éditoriaux validés par l'utilisateur, appliqués par /creer et contrôlés par `outils/verifier.py`. Ce sont des décisions, pas des preuves ; les ids entre crochets renvoient aux mécaniques qui les fondent.
> 3. **Conformité** et **repères externes** (presse, guides : non mesurés par nos analyses).
> On garde les MÉCANIQUES, jamais le texte des autres.

<!-- BIBLIOTHEQUE:DEBUT -->
## Bibliothèque des mécaniques (générée le 24/11/2026 : 72 vidéos, 15 comptes)
> Section réécrite par `python3 outils/mecaniques.py` depuis `bible/mecaniques.json` (fiche complète de chaque mécanique : effet, fonctionnement, conditions, variantes, erreurs, sources). Chiffres détaillés : `analyses/MECANIQUES.md`.
> Niveaux : à tester (1 compte ou moins de 3 histoires) · récurrente (2+ comptes, 3+ histoires) · fortement documentée (4+ comptes, 6+ histoires, 3 fiches v2 vérifiées, performance mesurée sur 4+ comptes). « Plus/moins vue » = dans son propre compte, hors suites : une corrélation, jamais une preuve de cause. Rien ici n'est obligatoire.

### Ce qu'on retrouve souvent (socle du genre)
- **Le spectateur sait, les personnages non** (`ironie_dramatique`, narration) — récurrente (confiance moyenne), 30 vidéos, 13 comptes · plus vue dans son compte (×1,82, 9 comptes), mais s'inverse en partie 1 ×0,84.
- **Injustice publique contre le héros qu'on aime** (`humiliation_injuste`, emotion) — récurrente (confiance moyenne), 21 vidéos, 13 comptes · plus vue dans son compte (×1,94, 10 comptes), mais s'inverse en vidéo unique ×0,94.
- **Couper la vidéo au seuil de la révélation** (`coupure_avant_payoff`, retention) — récurrente (confiance moyenne), 22 vidéos, 13 comptes · pas d'écart net de vues dans son compte (×1,21, 10 comptes).
- **Le méprisé se révèle supérieur devant ceux qui l'ont méprisé** (`renversement_statut`, emotion) — récurrente (confiance moyenne), 24 vidéos, 12 comptes · plus vue dans son compte (×1,37, 8 comptes), mais s'inverse en vidéo unique ×0,77.
- **Série en parties avec reprise exacte de la fin** (`suite_partie_n`, format) — récurrente (confiance moyenne), 20 vidéos, 11 comptes · effet sur les vues non mesurable (moins de 2 comptes où comparer).
- **Un gros chiffre lisible dans l'image** (`chiffre_ecran`, realisation) — récurrente (confiance moyenne), 13 vidéos, 9 comptes · plus vue dans son compte (×1,35, 5 comptes), stable dans tous les sous-groupes.
- **Une règle absurde du monde annoncée à 0 s** (`regle_du_monde`, hook) — récurrente (confiance moyenne), 11 vidéos, 6 comptes · pas d'écart net de vues dans son compte (×1,56, 4 comptes).
- **Une question ou un appel adressé au spectateur** (`question_au_spectateur`, interaction) — récurrente (confiance moyenne), 9 vidéos, 6 comptes · plus vue dans son compte (×2,45, 5 comptes), écart non net en hors ton noir ×1,65.
- **Un tiers vulnérable fait monter l'enjeu** (`proche_en_danger`, emotion) — récurrente (confiance moyenne), 8 vidéos, 5 comptes · pas d'écart net de vues dans son compte (×1,3, 4 comptes).
- **Le héros pourrait riposter mais s'en empêche** (`retenue_volontaire`, narration) — récurrente (confiance moyenne), 3 vidéos, 3 comptes · pas d'écart net de vues dans son compte (×1,02, 3 comptes).

### Mérite d'être testé
- **L'information change de camp une seconde fois** (`double_retournement`, retention) — 2 vidéos, 2 comptes · manque 1 histoire indépendante de plus.
- **Un témoin réagit juste après la réplique-choc** (`temoin_reaction`, montage) — 1 vidéo, 1 compte · manque 1 compte de plus, 2 histoires indépendantes de plus.
- **Compilation « le film » d'une série terminée** (`compilation_film`, format) — 1 vidéo, 1 compte · manque 1 compte de plus, 2 histoires indépendantes de plus.

### Dépend du contexte
- **Une question binaire posée tôt, tranchée à la fin** (`epreuve_verdict`, retention) — récurrente (confiance moyenne), 17 vidéos, 10 comptes · moins vue dans son compte (×0,69, 6 comptes), mais s'inverse en vidéo unique ×1,19. Garder l'épreuve comme moteur mais l'adosser à une identité révélée ou une force cachée ; jamais seule.
- **Tension muette, plans courts, peu de mots** (`style_muet`, montage) — récurrente (confiance moyenne), 8 vidéos, 2 comptes · effet sur les vues non mesurable (moins de 2 comptes où comparer). Pas de style par défaut : silence pour la menace physique, parole continue pour les conflits sociaux ; la règle « 55 % de parole par plan » reste sauf plan muet volontaire.
- Ton « drame » — 14 comptes · plus vue dans son compte (×1,51, 11 comptes), écart non net en partie 1 ×2,55, vidéo unique ×1, hors ton noir ×1,02.
- Ton « noir » — 8 comptes · moins vue dans son compte (×0,54, 8 comptes), écart non net en vidéo unique ×0,99.
- Ton « horreur » — 2 comptes · plus vue dans son compte (×1,86, 2 comptes), écart non net en hors ton noir ×1,06.
- Domaine « couple » — 10 comptes · plus vue dans son compte (×1,38, 10 comptes), mais s'inverse en partie 1 ×0,84, vidéo unique ×0,94, hors ton noir ×0,87.
- Domaine « famille » — 8 comptes · moins vue dans son compte (×0,51, 8 comptes), écart non net en hors ton noir ×0,85.
- Domaine « concours » — 3 comptes · moins vue dans son compte (×0,71, 3 comptes), écart non net en vidéo unique ×0,88.
- Domaine « sport » — 3 comptes · plus vue dans son compte (×1,52, 3 comptes), écart non net en partie 1 ×3,21.
- Numéroter « Partie 1 » fait-il des vues ? → Non démontré : ne pas numéroter pour faire des vues ; numéroter seulement quand une suite est prévue.

### À éviter
- Aucun facteur négatif stable mesuré à ce jour.
- Erreurs connues : champ `erreurs` de chaque mécanique (`bible/mecaniques.json`) et section « Conformité » de ce fichier.

Aucune mécanique fortement documentée : les codages viennent surtout des fiches v1 non vérifiées. Les plus proches : `ironie_dramatique` (manque fiches v2 vérifiées 2/3 dans 2/2 comptes) ; `humiliation_injuste` (manque fiches v2 vérifiées 2/3 dans 2/2 comptes) ; `coupure_avant_payoff` (manque fiches v2 vérifiées 2/3 dans 2/2 comptes).
<!-- BIBLIOTHEQUE:FIN -->

## Règles de fabrication (validées par l'utilisateur)

### Principe de transposition
Histoires HUMAINES (test d'amour, faux pauvre, belle-famille, revanche, caïd humilié) ; les animaux sont le casting et vivent comme des humains.
L'espèce sert au look et au caractère. **Assoupli le 23/11/2026** : la nature de l'animal peut servir de ressort si le drame reste humain et donne une image choc lisible en 1 s (bébé d'une espèce impossible = soupçon de tromperie). Jamais une blague de biologie sans enjeu humain.
Les pitchs de /creer sont des REMIX (squelette prouvé + 1-2 greffes + nouveau domaine, grille « GROS ») : `bible/histoires.json`.

### Moteur d'histoire (obligatoire, retour utilisateur 22/11/2026 : « pas intéressant »)
Une suite de gags ne tient pas. Ce qui tient 75 s : le spectateur VEUT voir quelque chose arriver.
1. **Injustice dans les 10 premières secondes** : le héros (qu'on aime) se fait humilier, voler, écraser par un antagoniste odieux et puissant. [`humiliation_injuste`]
2. **Ironie dramatique** : le spectateur sait le secret du héros, les méchants non. [`ironie_dramatique`]
3. **Antagoniste à détester** : il humilie EN PUBLIC, triche, méprise, et a une réplique-signature arrogante qui reviendra contre lui.
4. **Enjeu chiffré qui monte** : un chiffre lisible (contrat 1 M€, 5 000 €, 34 ans) et chaque plan rend la situation pire. [`chiffre_ecran`]
5. **Force cachée montrée une fois au milieu** : le héros prouve sa valeur, le méchant devient jaloux et triche. [`retenue_volontaire`]
6. **Retournement = l'info change de camp**, pas un nouveau gag.
7. **Payoff satisfaisant** : le méchant est puni par SA PROPRE ARME / sa propre réplique (callback), devant tout le monde. [`renversement_statut`]
8. **Kicker final** : une dernière info qui relance + question de vote morale (« il avait le droit ? »). [`question_au_spectateur`]

### Écriture des dialogues
- Chaque réplique a une FONCTION : attaque, riposte, revelation, reaction, menace, promesse, aveu. Jamais « info ».
- **Clash** : attaque → riposte immédiate. La riposte doit être meilleure que l'attaque.
- Phrases parlées, courtes, rythmées, qu'on a envie de citer en commentaire. Sous-texte > explication.
- Le méchant a une phrase-signature → le héros la lui renvoie au payoff.
- Témoin qui dit tout haut ce que pense le spectateur, 1-3 mots, juste après la réplique-choc. [`temoin_reaction`]
- Parole quasi continue : au moins 55 % de chaque plan parlé, jamais plus de 1,5 s de silence, sauf plan muet volontaire (menace physique, face-à-face : voir la contradiction « parole_vs_muet »).

### Structure de rétention
| Temps | Plan | Rôle |
|---|---|---|
| 0-2 s | 1 | Réplique-choc au cœur du conflit + texte d'accroche à l'écran (7 mots max). Jamais de contexte avant. |
| 6-12 s | 2 | Contexte en une phrase pour ceux qui arrivent au milieu d'une série. |
| 12-30 s | 3-5 | Escalade, 1er retournement avant 35 s. |
| ~30-45 s | 5-8 | Question au milieu en texte à l'écran (« Tu la crois, toi ? »). |
| 35-60 s | 6-10 | 2e retournement : l'information change de camp. |
| 60-70 s | 11-12 | Climax puis coupure au pire moment, après avoir payé quelque chose dans la vidéo. [`coupure_avant_payoff`] |
| fin | — | Question de vote, commentaire épinglé identique ; « Partie N+1 ? » seulement si une suite est prévue. L'épisode suivant reprend le choix gagnant et le DIT. |

### Machine virale v2 (réalisation Grok, 22/11/2026)
- **Rupture toutes les 2-3 s** : un plan Grok = plusieurs temps forts timecodés (action, réaction, coup de caméra, bruitage). Jamais une seule action molle sur 6 s.
- **Ping-pong** : 2 personnages se répondent dans le même plan (attaque → réplique → réaction du témoin). Répliques de 1 à 12 mots.
- **Durées variées** : plans de 6 s (punch) et de 10 s (révélation, humiliation, climax) avec image de DÉBUT + image de FIN.
- **Grok** : segments timecodés « [0-2s] … », décrire le son autant que l'image (il génère voix + bruitages), 1-2 phrases par réplique. Actions simples et lisibles (pointer, se lever, claquer une porte) : Grok anime mal les actions complexes, l'histoire passe par les dialogues.
- **Style cartoon 3D stylisé** (jamais photoréaliste) : lisible sur téléphone, émotions en 0,5 s. Étiquette « généré par IA » activée.
- **Texte dans le décor** : tableau, banderole, maillot avec noms fictifs = contexte compris sans voix off.
- **Hooks A/B** : 3 hooks de rechange par vidéo ; si < 2 000 vues en 2 h, refaire seulement le plan 1 et reposter. Noter le résultat dans `tests_ab` de la mécanique testée.
- **Univers étendu** : mêmes familles et clubs fictifs d'une vidéo à l'autre.
- **Durée** : 61 à 75 s (au-delà d'1 min = éligible aux Récompenses Créateurs).

## Conformité (cause probable des 2 vidéos bannies)
La bible imposait « espèce de bâtard » et les épisodes contenaient « garce », « trop con » : TikTok transcrit les voix et
classe les insultes dégradantes en harcèlement. Tout est filtré par `conformite.json` (rouge = bloqué, orange = 2 max).

## Repères externes (novembre 2026, non mesurés par nos analyses)
Sources : Fruit Love Island (Ai Cinema, ~10 M de vues par épisode), articles NBC / Wired sur les « fruit dramas », guides algorithme TikTok 2026 (Sendible, eClincher, OpusClip, Socialync), aide TikTok « contenu généré par IA ». Consensus de blogs, pas de données officielles.
- **Concept lisible en 1 seconde** : un personnage reconnaissable + un format connu (télé-réalité, soap, procès). Chaque personnage = son animal + accessoires qui disent son caractère.
- **Thèmes cités** : tromperie, trahison, triangle amoureux, héritage/argent, belle-famille. Absurde assumé.
- **Signaux de l'algorithme** : complétion (~70 % visé) et revisionnages, puis partages et enregistrements, commentaires, likes. Test sur un petit public puis élargissement si les premières heures sont bonnes : les 2 premières secondes et l'absence de temps mort comptent le plus.
