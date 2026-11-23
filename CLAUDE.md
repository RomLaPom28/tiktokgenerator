# Studio animaux — consignes pour Claude

Mode d'emploi complet : `MODE-EMPLOI.md`. Commandes : `/copier`, `/creer`, `/episode`, `/monter`, `/analyser`, `/studio` (skills dans `.claude/skills/`).

## Règles permanentes (validées par l'utilisateur)
- **Toujours de zéro** : toute nouvelle vidéo passe par `/creer` ou `/copier` (1. unique ou série → 2. sujet choisi ensemble → 3. tout générer → 4. prompts ChatGPT + Grok). Aucun personnage/décor repris d'un autre projet. `/episode` sert seulement à continuer une série existante. Ne jamais supprimer un ancien projet.
- **Copier une vidéo qui a percé** : `/copier <lien|id>` découpe la vidéo (personnages, décors, répliques attribuées, pourquoi ça marche, améliorations), propose 3 transpositions, puis recrée l'histoire réplique par réplique (même fonction, même place, autres mots) avec d'autres personnages et décors. Aucune réplique recopiée (le vérificateur bloque à 70 % de ressemblance), aucun nom propre de la source.
- **Sujets = remix de ce qui a marché** : `/creer` part de `bible/histoires.json` (squelette prouvé + greffes + nouveau domaine), note 12 pitchs avec la grille « GROS » et n'en montre que 4. Le foot n'est pas le domaine par défaut.
- **Histoire = moteur d'émotion** : remplir `moteur` (désir, injustice, antagoniste, enjeu chiffré, force cachée, payoff, callback, kicker) avant les plans. Un méchant qu'on déteste, une humiliation injuste, payoff par sa propre phrase (callback). Pas une suite de gags. Dialogues en clashs (attaque → riposte, 4+), parole continue.
- **Style** : animation 3D cartoon stylisée (grands yeux, expressions exagérées, couleurs saturées, décors pleins de figurants, textes/chiffres fictifs dans le décor). Jamais photoréaliste. Plans de 6 et 10 s (image de fin pour les 10 s), dialogues timecodés, ping-pong, rupture toutes les 2-3 s. Modèle : `projets/faux-joueur-district/episodes/ep001/episode.json`.
- **Prénoms** : majorité de prénoms français classiques adaptés à l'âge (Lucas, Hugo, Chloé, Manon, Sandrine…), au maximum UN prénom d'origine étrangère par casting.
- **Page de prompts** : `pack.html` affiche les prompts en clair (jamais seulement des boutons). Ne pas revenir à l'ancien format de `outils/pack.py`.

## Où ça tourne
- **PC (Windows)** : tout fonctionne. Ouvrir `pack.html` avec `Start-Process`. `/monter` et `/analyser` ont besoin de ffmpeg, yt-dlp, faster-whisper et du dossier Téléchargements : **PC uniquement**.
- **Cloud / téléphone (Linux, pas de `C:\`)** : `/creer`, `/episode` et `/copier` (sur une vidéo déjà analysée) marchent (Python seul, `python3 outils/verifier.py` et `python3 outils/pack.py`). Pas de navigateur : à la fin, **afficher dans la réponse les prompts prêts à copier** (portraits, ouverture, puis Image N / Vidéo N, légende, commentaire épinglé), lus depuis `pack.json`. Puis commit + push de la branche pour que le PC récupère le projet (`git pull` / merge). `/monter` et `/analyser` : répondre que ça se fait depuis le PC.
- Vidéos (`*.mp4`) et audio ne sont pas dans le dépôt (trop lourds) : `sources/videos/` reste sur le PC, les `analyses/*/fiche.md`, `brut.json` et planches suffisent pour `/creer`.
