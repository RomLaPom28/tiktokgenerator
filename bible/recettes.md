# Recettes virales (apprises des analyses)

> /analyser complète ce fichier après chaque lot de vidéos analysées (section « Mécaniques consolidées », tirée de `bible/mecaniques.json`).
> On garde les MÉCANIQUES (structure, rythme, types d'accroche), jamais le texte des autres.

## Base de départ (avant analyses)
- Accroche : la 1re réplique dit le drame, pas le contexte. Ex. de mécanique : « Je te trompe depuis 3 ans » dès la 1re seconde.
- Rythme : un plan toutes les 5 à 6 s (contrainte Grok), une réplique par plan, jamais de silence de plus de 1 s.
- Retournement : toutes les 15 à 20 s, l'information change de camp.
- Fin : coupure au moment où quelqu'un va révéler / frapper / ouvrir la porte.
- Interaction : question binaire en dernier plan et en commentaire épinglé (« Il pardonne ou il part ? »).

## Appris de la recherche (novembre 2026)
Sources : Fruit Love Island (Ai Cinema, lancé le 13/03/2026, ~10 M de vues par épisode, 3 M d'abonnés en une saison),
articles NBC / Wired sur les « fruit dramas », guides algorithme TikTok 2026, Règles de la communauté TikTok (24/09/2026).
- **Concept lisible en 1 seconde** : un objet/animal reconnaissable + un format télé connu (télé-réalité, soap, procès).
  Chez nous : animaux de ferme + drame de quartier français. Chaque personnage = son animal + accessoires qui disent son caractère.
- **Thèmes qui marchent** : tromperie, trahison, triangle amoureux, héritage/argent, belle-famille. Absurde assumé.
- **Format série** : épisodes courts, numérotés « Partie N », fin sur cliffhanger, même casting, playlist sur le profil.
  Les gens arrivent au milieu de la série : le plan 2 doit redonner le contexte en une phrase.
- **Vote du public** : une question d'opinion (« Tu es team qui ? ») en fin d'épisode + commentaire épinglé ; l'épisode suivant reprend le choix gagnant et le DIT.
- **Algorithme** (consensus des guides, pas de chiffres officiels) : 1) taux de complétion / temps de visionnage, 2) revisionnages,
  3) partages et enregistrements, 4) commentaires, 5) likes. Test sur un petit public puis élargissement si les 1res heures sont bonnes.
  → tout se joue sur : les 2 premières secondes, AUCUN temps mort, et une fin qui donne envie de revoir / de commenter.
- **Durée** : 61 à 75 s (au-delà d'1 min = éligible aux Récompenses Créateurs ; 12 plans × 6 s coupés serré).
- **Discours > animation** : Grok anime mal les actions complexes → l'histoire passe par les DIALOGUES (engueulades, mépris, aveux),
  avec des actions simples et lisibles (pointer, se lever, claquer une porte, téléphone qui vibre).

## Structure de rétention (appliquée à chaque épisode)
| Temps | Plan | Rôle |
|---|---|---|
| 0-2 s | 1 | Réplique-choc au cœur du conflit + texte d'accroche à l'écran (7 mots max). Jamais de contexte avant. |
| 6-12 s | 2 | Contexte en une phrase pour les nouveaux (« Depuis qu'il a gagné… »). |
| 12-30 s | 3-5 | Escalade, 1er retournement avant 35 s. |
| ~30-45 s | 5-8 | **Question au milieu** en texte à l'écran (« Tu la crois, toi ? ») : relance l'attention et les commentaires. |
| 35-60 s | 6-10 | 2e retournement : l'information change de camp. |
| 60-70 s | 11-12 | Climax puis coupure au pire moment (phrase interrompue, coup qui part, porte qui s'ouvre). |
| fin | — | Texte « Partie N+1 ? » + question de vote, commentaire épinglé identique. |

## Conformité (cause probable des 2 vidéos bannies)
La bible imposait « espèce de bâtard » et les épisodes contenaient « garce », « trop con » : TikTok transcrit les voix et
classe les insultes dégradantes en harcèlement. Tout est maintenant filtré par `conformite.json` (rouge = bloqué, orange = 2 max).


## Mécaniques consolidées (24/11/2026 — registre `bible/mecaniques.json`, rapport `analyses/MECANIQUES.md`)
72 vidéos, 15 comptes, tout en « fruit drama » FR. Regénéré par `python3 outils/mecaniques.py` ; cette section le résume.
**Lire avant d'utiliser** : *confiance* = récurrence sur des comptes indépendants (faible 1 · moyen 2-3 · élevé 4+).
*Signal* = vues avec ÷ sans la mécanique dans le même compte, hors suites ; *fragile* = s'inverse en partie 1 seule,
en vidéos uniques seules ou hors ton noir. Tout est corrélation : aucune mécanique n'est prouvée CAUSE de vues.

Récurrence élevée (le genre les utilise partout : les respecter est le minimum, pas un avantage) :
1. **Ironie dramatique** (`ironie_dramatique`) — élevé, 13 comptes · signal fragile. Donner le secret au spectateur avant 10 s. Variante la plus associée aux vues : statut caché montré (`identite_cachee`, ×2,7, 4 comptes). L'aveu parlé à 0 s n'a pas d'effet mesurable (×1,07).
2. **Injustice publique** (`humiliation_injuste`) — élevé, 13 comptes · signal fragile. Humilier le héros devant témoins avant 15 s, escalade. Limite : seule, sans promesse de revanche, elle ne tient pas.
3. **Renversement de statut** (`renversement_statut`) — élevé, 12 comptes · signal fragile. Payer devant les mêmes témoins. Variantes associées à plus de vues : force cachée (×2,0) et identité révélée ; le glow-up montré est en dessous (×0,71, 4 comptes).
4. **Coupure au seuil du payoff** (`coupure_avant_payoff`) — élevé, 13 comptes · signal neutre. Utile pour la suite, mais les suites ne font que 30 à 70 % des vues de la partie 1 (6 séries).
5. **Gros chiffre dans l'image** (`chiffre_ecran`) — élevé, 9 comptes · **seul signal positif robuste** (×1,35, 5 comptes). Le moins cher à appliquer : un chiffre énorme lisible dans le décor ou sur le personnage.
6. **Règle absurde du monde à 0 s** (`regle_du_monde`) — élevé, 6 comptes · neutre. La variante « valeur chiffrée affichée » recoupe le n° 5.
7. **Proche vulnérable en danger** (`proche_en_danger`) — élevé, 5 comptes · neutre. Lève la retenue du héros ; ne pas montrer la violence.

Récurrence moyenne ou faible (à tester, pas à imposer) :
8. **Retenue volontaire** (`retenue_volontaire`) — moyen, 3 comptes. Une phrase qui explique pourquoi le héros encaisse.
9. **Style muet** (`style_muet`) — moyen, 2 comptes (clip.drama.ia, fruitdeguerre), tous deux lycée/rue/bagarre : style et thème confondus. Engagement élevé, vues plus faibles.
10. **Témoin qui réagit** (`temoin_reaction`) — faible : codé sur 1 vidéo. Bonne pratique de réalisation, pas une preuve.
11. **Compilation « le film »** (`compilation_film`) — faible : 1 cas (7 M). Les « épisodes complets » inédits de 5-10 min sont faibles (médiane 0,67 M).

Contradictions et pièges :
- **Épreuve / test d'amour** (`epreuve_verdict`) : très fréquent (10 comptes) mais signal NÉGATIF (×0,69, test d'amour ×0,74). Corrige l'ancienne recette « test d'amour 9/12 > 1 M » : ce chiffre venait d'un corpus fait du top de chaque compte. Le test reste un bon moteur s'il est combiné à une identité révélée, pas seul.
- **« Partie 1 » ×2,05 contre « unique » ×0,41** : causalité probablement inversée (une vidéo qui perce DEVIENT une partie 1 parce que le créateur fait une suite). Ne pas en déduire qu'il faut numéroter.
- La plupart des signaux positifs disparaissent quand on sépare partie 1 et vidéos uniques : le format et le ton expliquent une bonne part des écarts. Seul le gros chiffre à l'écran tient dans tous les sous-groupes.
- Anciennes affirmations retirées faute de preuve : « 13/13 > 1 M » pour l'aveu (biais de sélection), « témoin présent dans les 7 vidéos à 0,2 % de com » (1 seule vidéo codée).

Facteurs de contexte :
- Ton **noir** : signal négatif robuste (×0,54, 8 comptes). Le drame humain reste la base.
- Domaine **famille** (souvent associé au ton noir dans le corpus) : ×0,51, 8 comptes. **Couple** : ×1,38 mais fragile.
- Suites : 30 à 70 % des vues de la partie 1. Chaque partie 1 doit tenir seule.
- Le principe de transposition reste : histoires HUMAINES, animaux = casting. **Règle assouplie (23/11/2026)** : la nature de l'animal PEUT servir de ressort si le drame reste humain et que ça donne une image choc lisible en 1 s. Jamais une blague de biologie sans enjeu humain.

Prochaine étape pour passer de corrélation à cause : nos tests A/B (même histoire, avec et sans chiffre à l'écran ; avec identité révélée contre glow-up), notés dans `tests_ab` du registre.


## Machine virale v2 (recherche 22/11/2026 + retours utilisateur)
Sources : guides algorithme TikTok 2026 (Sendible, eClincher, OpusClip, Socialync), aide TikTok « contenu généré par IA »,
guides de prompts Grok Imagine (fal.ai, Replicate, Morphic). Chiffres = consensus de blogs, pas de données officielles TikTok.
- **Signaux** : complétion (~70 % visé) et REVISIONNAGES (le plus fort en 2026 selon plusieurs guides) → fin qui boucle sur le début.
- **Rupture toutes les 2-3 s** : un plan Grok = plusieurs temps forts timecodés (action, réaction, coup de caméra, bruitage).
  Jamais une seule action molle sur 6 s.
- **Ping-pong** : 2 personnages se répondent dans le même plan (attaque → réplique → réaction du témoin). Répliques de 1 à 12 mots.
- **Durées variées** : plans de 6 s (punch) et de 10 s (scènes clés : révélation, humiliation, climax) avec image de DÉBUT + image de FIN.
- **Grok** : écrire en segments timecodés « [0-2s] … », décrire le son autant que l'image (il génère voix + bruitages), 1-2 phrases par réplique.
- **Style cartoon 3D stylisé** (pas photoréaliste) : plus lisible sur téléphone, expressions exagérées = émotions en 0,5 s,
  et TikTok exige l'étiquette IA surtout pour le contenu RÉALISTE. On active quand même l'étiquette « généré par IA ».
- **Texte dans le décor** : tableau d'affichage, banderole, maillot avec noms fictifs = contexte compris sans voix off.
- **Hooks A/B** : 3 hooks de rechange par vidéo ; si < 2 000 vues en 2 h, on refait seulement le plan 1 et on reposte.
- **Univers étendu** : mêmes clubs/familles fictifs d'une vidéo à l'autre = le public reconnaît la « marque ».


## Banque d'histoires (23/11/2026)
Les pitchs de /creer sont des REMIX : un squelette prouvé + 1-2 greffes d'autres vidéos + un nouveau domaine, notés avec la grille « GROS » (image choc, enjeu vital, faute grave du méchant, scène attendue, retournement de camp, preuve). Tout est dans `bible/histoires.json`.

## Moteur d'histoire (obligatoire, retour utilisateur 22/11/2026 : « pas intéressant »)
Une suite de gags ne tient pas. Ce qui tient 75 s : le spectateur VEUT voir quelque chose arriver.
1. **Injustice dans les 10 premières secondes** : le héros (qu'on aime) se fait humilier/voler/écraser par un antagoniste odieux et puissant.
2. **Ironie dramatique** : le spectateur sait le secret du héros (aveu à 0 s), les méchants non → il attend la révélation.
3. **Antagoniste à détester** : il humilie EN PUBLIC, triche, méprise, et a une réplique-signature arrogante qui reviendra contre lui.
4. **Enjeu chiffré qui monte** : un chiffre lisible (contrat 1 M€, 5 000 €, 34 ans) et chaque plan rend la situation pire.
5. **Force cachée montrée une fois au milieu** : le héros prouve sa valeur (geste spectaculaire), le méchant devient jaloux et triche.
6. **Retournement = l'info change de camp**, pas un nouveau gag.
7. **Payoff satisfaisant** : le méchant est puni par SA PROPRE ARME / sa propre réplique (callback), devant tout le monde.
8. **Kicker final** : une dernière info qui relance (twist, double secret) + question de vote morale (« il avait le droit ? »).

## Écriture des dialogues
- Chaque réplique a une FONCTION : attaque, riposte, revelation, reaction, menace, promesse, aveu. Jamais « info ».
- **Clash** : attaque → riposte immédiate (vanne → contre-vanne). La riposte doit être meilleure que l'attaque.
- Phrases parlées, courtes, rythmées, qu'on a envie de citer en commentaire. Sous-texte > explication.
- Le méchant a une phrase-signature (« Les vieux, chez moi, ça finit sur le banc ») → le héros la lui renvoie au payoff.
- Témoin qui dit tout haut ce que pense le spectateur, 1-3 mots, juste après la réplique-choc.
- Parole quasi continue : au moins 55 % de chaque plan parlé, jamais plus de 1,5 s de silence (sauf plan muet volontaire).
