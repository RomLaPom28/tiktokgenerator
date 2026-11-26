# Écrase-la — Partie 1 : prompts

Durée totale : 88 s · Accroche : Elle a renversé ma sœur

## 0. Portraits de référence (ChatGPT, un par personnage, à enregistrer dans refs/)

### Lucas → `refs/lucas.png`

```
Fiche de référence personnage : Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture. Plan en pied de trois quarts face, pose de personnage de film d'animation pleine d'attitude, expression typique de son caractère (génie de la mécanique, taiseux, encaisse puis frappe avec une phrase), fond uni dégradé chaud, lumière studio douce. Qualité : personnage de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon, grands yeux brillants, silhouette ultra reconnaissable, couleurs saturées, aucun décor ni figurant. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Vertical 9:16, aucun texte, aucun logo.
```

### Jade → `refs/jade.png`

```
Fiche de référence personnage : Jade, lapine blanche de 16 ans aux très longues oreilles dont une bandée, grands yeux bleus, plâtre rose au bras droit couvert de dessins au feutre, blouse d'hôpital bleu ciel à petits motifs, bracelet d'hôpital au poignet. Plan en pied de trois quarts face, pose de personnage de film d'animation pleine d'attitude, expression typique de son caractère (douce, drôle avant l'accident, aujourd'hui silencieuse), fond uni dégradé chaud, lumière studio douce. Qualité : personnage de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon, grands yeux brillants, silhouette ultra reconnaissable, couleurs saturées, aucun décor ni figurant. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Vertical 9:16, aucun texte, aucun logo.
```

### Michel → `refs/michel.png`

```
Fiche de référence personnage : Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées. Plan en pied de trois quarts face, pose de personnage de film d'animation pleine d'attitude, expression typique de son caractère (bourru et tendre, a tout donné pour élever ses petits-enfants, à bout), fond uni dégradé chaud, lumière studio douce. Qualité : personnage de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon, grands yeux brillants, silhouette ultra reconnaissable, couleurs saturées, aucun décor ni figurant. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Vertical 9:16, aucun texte, aucun logo.
```

### Dylan → `refs/dylan.png`

```
Fiche de référence personnage : Dylan, lévrier afghan de 21 ans au long pelage doré brushé comme une coiffure de star, museau fin relevé, lunettes de soleil miroir, grosse chaîne en or, veste en cuir blanc immaculé, tee-shirt noir, jean clair, baskets blanches de luxe. Plan en pied de trois quarts face, pose de personnage de film d'animation pleine d'attitude, expression typique de son caractère (fils à papa, méprise les pauvres, lâche dès qu'il a peur), fond uni dégradé chaud, lumière studio douce. Qualité : personnage de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon, grands yeux brillants, silhouette ultra reconnaissable, couleurs saturées, aucun décor ni figurant. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Vertical 9:16, aucun texte, aucun logo.
```

### Christophe → `refs/christophe.png`

```
Fiche de référence personnage : Christophe, taureau noir massif de 52 ans, cornes polies et brillantes, anneau doré au museau, grosse chevalière en or à la main droite, costume trois pièces bordeaux sur mesure, cravate dorée, montre en or. Plan en pied de trois quarts face, pose de personnage de film d'animation pleine d'attitude, expression typique de son caractère (roi des concessions de la région et adjoint au maire, sourit en menaçant), fond uni dégradé chaud, lumière studio douce. Qualité : personnage de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon, grands yeux brillants, silhouette ultra reconnaissable, couleurs saturées, aucun décor ni figurant. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Vertical 9:16, aucun texte, aucun logo.
```

### Nathalie → `refs/nathalie.png`

```
Fiche de référence personnage : Nathalie, pie de 47 ans au plumage noir et blanc à reflets bleus, gros bigoudis roses sur la tête, longues boucles d'oreilles en plastique, téléphone toujours à la main, tablier à grosses fleurs jaunes sur un pull violet, chaussons fourrés. Plan en pied de trois quarts face, pose de personnage de film d'animation pleine d'attitude, expression typique de son caractère (tient le snack en face de la casse, voit tout, filme tout, répète tout), fond uni dégradé chaud, lumière studio douce. Qualité : personnage de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon, grands yeux brillants, silhouette ultra reconnaissable, couleurs saturées, aucun décor ni figurant. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Vertical 9:16, aucun texte, aucun logo.
```

## 1. Message d'ouverture (nouvelle conversation ChatGPT, joindre les 6 portraits)

```
Tu vas générer les images d'une vidéo. Toutes les images : format vertical 9:16, même style, mêmes personnages avec EXACTEMENT les mêmes visages, couleurs et accessoires d'une image à l'autre. Aucun sous-titre ni bulle ; le seul texte autorisé est celui que je décris dans le décor (tableau d'affichage, banderole, maillot), écrit sans faute.

STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux.

PERSONNAGES DE CET ÉPISODE (looks fixes) :
- Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues. Tenue : salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture.
- Jade, lapine blanche de 16 ans aux très longues oreilles dont une bandée, grands yeux bleus, plâtre rose au bras droit couvert de dessins au feutre. Tenue : blouse d'hôpital bleu ciel à petits motifs, bracelet d'hôpital au poignet.
- Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre. Tenue : salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées.
- Dylan, lévrier afghan de 21 ans au long pelage doré brushé comme une coiffure de star, museau fin relevé, lunettes de soleil miroir, grosse chaîne en or. Tenue : veste en cuir blanc immaculé, tee-shirt noir, jean clair, baskets blanches de luxe.
- Christophe, taureau noir massif de 52 ans, cornes polies et brillantes, anneau doré au museau, grosse chevalière en or à la main droite. Tenue : costume trois pièces bordeaux sur mesure, cravate dorée, montre en or.
- Nathalie, pie de 47 ans au plumage noir et blanc à reflets bleus, gros bigoudis roses sur la tête, longues boucles d'oreilles en plastique, téléphone toujours à la main. Tenue : tablier à grosses fleurs jaunes sur un pull violet, chaussons fourrés.

Si je joins des images de référence, ce sont ces personnages : respecte-les à la lettre.
Je vais t'envoyer "Image 1 : …", "Image 2 : …". Pour chaque message, génère uniquement l'image demandée, sans commentaire. Réponds juste OK à ce message.
```

## 2. Plans

### Plan 1 · 6 s · accroche · La casse de Michel · TGP

Répliques : Lucas : « Cette voiture a renversé ma petite sœur. » / Lucas : « Elle est arrivée cette nuit. » / Lucas : « Pour se faire écraser. »

**Image 1 début** (ChatGPT)

```
Image 1 : très gros plan sur le visage, les yeux remplissent le cadre, caméra à hauteur des yeux. Décor : immense casse automobile en plein air, montagnes de carcasses de voitures rouillées empilées sur cinq étages, grue à pince jaune, presse hydraulique géante au centre, grande enseigne néon orange à moitié grillée « CASSE MICHEL & FILS », flaques d'huile, chiens de garde animaux au loin. Lumière : nuit bleutée au clair de lune. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : face caméra, un rétroviseur de scooter rose arraché dans la patte, mâchoire serrée, yeux brillants de rage. Derrière lui, une supercar fictive orange, la Falco GT, capot enfoncé et pare-brise étoilé, suspendue à la pince de la grue ; un éclat de plastique rose coincé dans sa calandre. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Seul texte visible, écrit lisiblement et sans faute dans le décor : papier scotché sur le pare-brise : « À ÉCRASER – PAYÉ ». Aucun sous-titre, aucune bulle, aucun vrai logo.
```

**Vidéo 1** (Grok, durée 6 s)

```
Vidéo verticale 9:16 de 6 secondes à partir de l'image jointe. Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-2s] Lucas se tourne d'un coup vers la caméra en levant le rétroviseur rose. Caméra : zoom éclair sur le visage au moment de la réplique-choc. Bruitage : whoosh.
[0.1-2.4s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, froid, à voix basse) dit en français : « Cette voiture a renversé ma petite sœur. »
[2-4s] La grue lâche la Falco au sol derrière lui dans un fracas de tôle. Bruitage : fracas métallique.
[2.6-4.0s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, sec) dit en français : « Elle est arrivée cette nuit. »
[4-6s] Lucas serre le rétroviseur, regard noir vers l'objectif. Caméra : secousse cartoon de la caméra à l'impact. Bruitage : note grave.
[4.2-5.9s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, glacial, regard caméra) dit en français : « Pour se faire écraser. »
Ambiance sonore : grincement de métal, grue hydraulique, chiens qui aboient au loin, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 2 · 6 s · developpement · Chambre de Jade à l'hôpital · PR

Répliques : Michel : « Vingt et un jours. Et la police a rien. » / Jade : « Je me souviens de rien. » / Lucas : « Moi, je vais me souvenir pour toi. »

**Image 2 début** (ChatGPT)

```
Image 2 : plan rapproché, de la tête à la poitrine, caméra en plongée, au-dessus, qui écrase le personnage. Décor : chambre d'hôpital lumineuse, lit à barreaux blancs, moniteur cardiaque qui bipe, dessins d'enfants scotchés au mur, ballons dégonflés, tableau blanc au mur, fenêtre sur la ville. Lumière : lumière naturelle de jour, ombres nettes. Jade, lapine blanche de 16 ans aux très longues oreilles dont une bandée, grands yeux bleus, plâtre rose au bras droit couvert de dessins au feutre, blouse d'hôpital bleu ciel à petits motifs, bracelet d'hôpital au poignet : allongée, oreille bandée, détourne les yeux, tire sur son oreille. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : assis au bord du lit, casquette à la main, épaules voûtées. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : debout près de la fenêtre, bras croisés, fixe sa sœur. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Seul texte visible, écrit lisiblement et sans faute dans le décor : tableau blanc au mur : « JADE, 16 ANS – JOUR 21 ». Aucun sous-titre, aucune bulle, aucun vrai logo.
```

**Vidéo 2** (Grok, durée 6 s)

```
Vidéo verticale 9:16 de 6 secondes à partir de l'image jointe. Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-3s] Michel tourne sa casquette entre ses pattes, regard vers le moniteur. Bruitage : bip du moniteur.
[0.2-2.6s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, las, rocailleux) dit en français : « Vingt et un jours. Et la police a rien. »
[2.8-4.0s] JADE (voix de jeune fille de 16 ans, douce et fatiguée, hésitante, petite voix, ment) dit en français : « Je me souviens de rien. »
[3-6s] Jade tire sur son oreille bandée et évite le regard de Lucas. Caméra : lent travelling avant vers le visage.
[4.1-5.9s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, doux mais ferme) dit en français : « Moi, je vais me souvenir pour toi. »
Ambiance sonore : bip régulier du moniteur, couloir d'hôpital, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 3 · 10 s · developpement · La casse de Michel · PA

Répliques : Dylan : « C'est toi, le ferrailleur ? » / Lucas : « C'est toi, le chauffard ? » / Nathalie : « QUOI ?! » / Dylan : « Cent mille euros. Tu l'écrases devant moi. » / Dylan : « Ce qui est cassé, on l'écrase. »

**Image 3 début** (ChatGPT)

```
Image 3 : plan américain, de la tête aux genoux, caméra en contre-plongée, en dessous, qui rend le personnage imposant. Décor : immense casse automobile en plein air, montagnes de carcasses de voitures rouillées empilées sur cinq étages, grue à pince jaune, presse hydraulique géante au centre, grande enseigne néon orange à moitié grillée « CASSE MICHEL & FILS », flaques d'huile, chiens de garde animaux au loin. Lumière : lumière dorée et douce du matin. Dylan, lévrier afghan de 21 ans au long pelage doré brushé comme une coiffure de star, museau fin relevé, lunettes de soleil miroir, grosse chaîne en or, veste en cuir blanc immaculé, tee-shirt noir, jean clair, baskets blanches de luxe : descend d'un SUV blanc rutilant, mallette argentée à la main, lunettes miroir baissées, sourire méprisant. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : face à lui, clé de 12 qui tourne entre ses doigts, regard fixe. Nathalie, pie de 47 ans au plumage noir et blanc à reflets bleus, gros bigoudis roses sur la tête, longues boucles d'oreilles en plastique, téléphone toujours à la main, tablier à grosses fleurs jaunes sur un pull violet, chaussons fourrés : au fond, plateau de frites à la main, bec grand ouvert. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Seul texte visible, écrit lisiblement et sans faute dans le décor : mallette ouverte pleine de billets avec un bandeau géant « 100 000 € ». Aucun sous-titre, aucune bulle, aucun vrai logo.
```

**Image 3 fin** (ChatGPT)

```
Image 3 FIN (dernière image du plan, quelques secondes plus tard) : plan rapproché, de la tête à la poitrine, caméra en contre-plongée, en dessous, qui rend le personnage imposant. Décor : immense casse automobile en plein air, montagnes de carcasses de voitures rouillées empilées sur cinq étages, grue à pince jaune, presse hydraulique géante au centre, grande enseigne néon orange à moitié grillée « CASSE MICHEL & FILS », flaques d'huile, chiens de garde animaux au loin. Lumière : lumière dorée et douce du matin. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : arrive en courant, yeux exorbités devant la mallette, le cure-dent tombe de sa bouche. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : poings serrés, lunettes de soudeur remontées d'un coup. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Seul texte visible, écrit lisiblement et sans faute dans le décor : mallette ouverte pleine de billets avec un bandeau géant « 100 000 € ». Aucun sous-titre, aucune bulle, aucun vrai logo.
```

**Vidéo 3** (Grok, durée 10 s)

```
Vidéo verticale 9:16 de 10 secondes à partir de l'image jointe (l'image de fin jointe est la dernière image à atteindre). Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-3s] Dylan claque la portière de son SUV blanc et essuie sa veste. Caméra : travelling latéral qui suit le personnage. Bruitage : portière qui claque.
[0.2-1.8s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, traînant, méprisant) dit en français : « C'est toi, le ferrailleur ? »
[2.0-3.2s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, calme, glacial) dit en français : « C'est toi, le chauffard ? »
[3-5s] Il ouvre la mallette d'un coup sec : des liasses de billets. Caméra : zoom éclair sur le visage au moment de la réplique-choc. Bruitage : clic de serrure.
[3.4-4.0s] NATHALIE (voix de femme de 47 ans, aiguë et rapide, adore les potins, cri aigu) dit en français : « QUOI ?! »
[4.3-6.6s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, sourire faux, ouvre la mallette) dit en français : « Cent mille euros. Tu l'écrases devant moi. »
[5-7s] Nathalie lâche son plateau de frites. Caméra : panoramique filé ultra rapide (whip pan) qui claque vers le personnage suivant. Bruitage : fracas de plateau.
[6.9-9.6s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, regarde Lucas de haut en bas) dit en français : « Ce qui est cassé, on l'écrase. »
[7-10s] Michel accourt, son cure-dent tombe devant la mallette. Bruitage : note de suspense.
Ambiance sonore : grincement de métal, grue hydraulique, chiens qui aboient au loin, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 4 · 6 s · retournement · La casse de Michel · GP

Répliques : Michel : « Marché conclu, petit. » / Lucas : « Papy ?! C'est la voiture de Jade. » / Michel : « On a quatre-vingt mille euros de dettes. »

**Image 4 début** (ChatGPT)

```
Image 4 : gros plan sur le visage et le haut des épaules, caméra à hauteur des yeux. Décor : immense casse automobile en plein air, montagnes de carcasses de voitures rouillées empilées sur cinq étages, grue à pince jaune, presse hydraulique géante au centre, grande enseigne néon orange à moitié grillée « CASSE MICHEL & FILS », flaques d'huile, chiens de garde animaux au loin. Lumière : lumière dorée et douce du matin. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : la patte posée sur la mallette, n'ose pas regarder Lucas, voix brisée. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : se retourne vers son grand-père, yeux exorbités, oreilles plaquées. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Aucun texte, aucun sous-titre, aucune bulle, aucun logo.
```

**Vidéo 4** (Grok, durée 6 s)

```
Vidéo verticale 9:16 de 6 secondes à partir de l'image jointe. Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-2s] Michel referme la mallette et serre la patte de Dylan. Caméra : panoramique filé ultra rapide (whip pan) qui claque vers le personnage suivant. Bruitage : claquement de mallette.
[0.2-1.6s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, sourd, sans regarder Lucas) dit en français : « Marché conclu, petit. »
[1.8-3.6s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, hurlé, trahi) dit en français : « Papy ?! C'est la voiture de Jade. »
[2-4s] Lucas se retourne d'un bond vers lui. Bruitage : whoosh.
[3.8-5.8s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, brisé, presque en pleurs) dit en français : « On a quatre-vingt mille euros de dettes. »
[4-6s] Michel baisse les yeux, mâchonne son cure-dent. Caméra : zoom éclair sur le visage au moment de la réplique-choc. Bruitage : note grave.
Ambiance sonore : grincement de métal, grue hydraulique, chiens qui aboient au loin, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 5 · 6 s · temoin · La casse de Michel · ECRAN

Répliques : Nathalie : « Il va vraiment l'écraser ?! » / Dylan : « Appuie, papy. Je paie pas pour regarder. » / Lucas : « T'as peur de quoi, Dylan ? D'une voiture ? »

**Image 5 début** (ChatGPT)

```
Image 5 : vue à travers l'écran d'un smartphone qui filme la scène, cadre vertical de téléphone, personnage de profil. Décor : immense casse automobile en plein air, montagnes de carcasses de voitures rouillées empilées sur cinq étages, grue à pince jaune, presse hydraulique géante au centre, grande enseigne néon orange à moitié grillée « CASSE MICHEL & FILS », flaques d'huile, chiens de garde animaux au loin. Lumière : lumière chaude et rasante de fin d'après-midi, longues ombres. Nathalie, pie de 47 ans au plumage noir et blanc à reflets bleus, gros bigoudis roses sur la tête, longues boucles d'oreilles en plastique, téléphone toujours à la main, tablier à grosses fleurs jaunes sur un pull violet, chaussons fourrés : filme avec son téléphone, aile plaquée sur le bec. Dylan, lévrier afghan de 21 ans au long pelage doré brushé comme une coiffure de star, museau fin relevé, lunettes de soleil miroir, grosse chaîne en or, veste en cuir blanc immaculé, tee-shirt noir, jean clair, baskets blanches de luxe : bras croisés devant la presse, tape du pied, impatient. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : planté entre la Falco et la presse, défie Dylan du regard. La Falco GT orange posée sur le plateau de la presse hydraulique géante. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Aucun texte, aucun sous-titre, aucune bulle, aucun logo.
```

**Vidéo 5** (Grok, durée 6 s)

```
Vidéo verticale 9:16 de 6 secondes à partir de l'image jointe. Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-3s] La Falco est poussée sur le plateau de la presse. Caméra : caméra à l'épaule, légèrement nerveuse. Bruitage : moteur hydraulique qui démarre.
[0.2-1.4s] NATHALIE (voix de femme de 47 ans, aiguë et rapide, adore les potins, chuchoté, excité) dit en français : « Il va vraiment l'écraser ?! »
[1.6-3.4s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, agacé, claque des doigts) dit en français : « Appuie, papy. Je paie pas pour regarder. »
[3-6s] Lucas se plante devant Dylan, nez à nez. Caméra : zoom éclair sur le visage au moment de la réplique-choc. Bruitage : grondement.
[3.6-5.9s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, sec, nez à nez) dit en français : « T'as peur de quoi, Dylan ? D'une voiture ? »
Ambiance sonore : grincement de métal, grue hydraulique, chiens qui aboient au loin, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 6 · 10 s · developpement · La casse de Michel · PE

Répliques : Michel : « Recule, Lucas ! » / Lucas : « Deux secondes, papy ! » / Nathalie : « NON ! » / Dylan : « Laisse-le, s'il veut finir en cube. » / Lucas : « Personne écrase ma sœur deux fois. » / Dylan : « Il a pris quoi, là ? »

**Image 6 début** (ChatGPT)

```
Image 6 : plan d'ensemble qui montre tout le décor et les personnages en pied, caméra en plongée, au-dessus, qui écrase le personnage. Décor : immense casse automobile en plein air, montagnes de carcasses de voitures rouillées empilées sur cinq étages, grue à pince jaune, presse hydraulique géante au centre, grande enseigne néon orange à moitié grillée « CASSE MICHEL & FILS », flaques d'huile, chiens de garde animaux au loin. Lumière : lumière chaude et rasante de fin d'après-midi, longues ombres. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : la patte sur le levier de la presse, hurle. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : plonge sous le plateau de la presse, bras tendu vers le pare-brise. Nathalie, pie de 47 ans au plumage noir et blanc à reflets bleus, gros bigoudis roses sur la tête, longues boucles d'oreilles en plastique, téléphone toujours à la main, tablier à grosses fleurs jaunes sur un pull violet, chaussons fourrés : téléphone levé, bec ouvert. Dylan, lévrier afghan de 21 ans au long pelage doré brushé comme une coiffure de star, museau fin relevé, lunettes de soleil miroir, grosse chaîne en or, veste en cuir blanc immaculé, tee-shirt noir, jean clair, baskets blanches de luxe : recule d'un pas, sourire figé. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Seul texte visible, écrit lisiblement et sans faute dans le décor : sur la presse, en lettres jaunes géantes : « PRESSE 300 TONNES ». Aucun sous-titre, aucune bulle, aucun vrai logo.
```

**Image 6 fin** (ChatGPT)

```
Image 6 FIN (dernière image du plan, quelques secondes plus tard) : plan rapproché, de la tête à la poitrine, caméra en plongée, au-dessus, qui écrase le personnage. Décor : immense casse automobile en plein air, montagnes de carcasses de voitures rouillées empilées sur cinq étages, grue à pince jaune, presse hydraulique géante au centre, grande enseigne néon orange à moitié grillée « CASSE MICHEL & FILS », flaques d'huile, chiens de garde animaux au loin. Lumière : lumière chaude et rasante de fin d'après-midi, longues ombres. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : à genoux dans la poussière, une minuscule carte mémoire entre deux doigts, sourire en coin. Dylan, lévrier afghan de 21 ans au long pelage doré brushé comme une coiffure de star, museau fin relevé, lunettes de soleil miroir, grosse chaîne en or, veste en cuir blanc immaculé, tee-shirt noir, jean clair, baskets blanches de luxe : lunettes miroir qui glissent du nez, visage pâle. Derrière eux, la Falco réduite en cube de métal. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Seul texte visible, écrit lisiblement et sans faute dans le décor : sur la presse, en lettres jaunes géantes : « PRESSE 300 TONNES ». Aucun sous-titre, aucune bulle, aucun vrai logo.
```

**Vidéo 6** (Grok, durée 10 s)

```
Vidéo verticale 9:16 de 10 secondes à partir de l'image jointe (l'image de fin jointe est la dernière image à atteindre). Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-2s] Michel abaisse le levier, la presse descend. Caméra : caméra fixe avec une secousse brève au moment de l'impact. Bruitage : sifflement hydraulique.
[0.2-1.2s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, hurlé) dit en français : « Recule, Lucas ! »
[1.5-2.8s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, crié, en plongeant) dit en français : « Deux secondes, papy ! »
[2-4s] Lucas plonge sous le plateau et arrache un petit boîtier du pare-brise. Caméra : ralenti dramatique d'une seconde puis reprise à vitesse normale. Bruitage : verre qui éclate.
[3.0-3.6s] NATHALIE (voix de femme de 47 ans, aiguë et rapide, adore les potins, hurlé) dit en français : « NON ! »
[4-6s] Il roule hors de la presse au dernier moment. Caméra : panoramique filé ultra rapide (whip pan) qui claque vers le personnage suivant. Bruitage : roulade dans la poussière.
[4.0-6.0s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, ricane, nerveux) dit en français : « Laisse-le, s'il veut finir en cube. »
[6-8s] La presse écrase la Falco en cube. Caméra : secousse cartoon de la caméra à l'impact. Bruitage : énorme craquement de tôle.
[6.2-7.8s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, se relève, glacial) dit en français : « Personne écrase ma sœur deux fois. »
[8-10s] Lucas se relève, carte mémoire entre les doigts. Caméra : zoom éclair sur le visage au moment de la réplique-choc.
[8.0-9.6s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, la voix qui déraille) dit en français : « Il a pris quoi, là ? »
Ambiance sonore : grincement de métal, grue hydraulique, chiens qui aboient au loin, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 7 · 6 s · developpement · Show-room Prestige Delmas · PR

Répliques : Dylan : « Papa, c'est fait. Elle est écrasée. » / Christophe : « Et la caméra de bord ? » / Dylan : « Quelle caméra ? »

**Image 7 début** (ChatGPT)

```
Image 7 : plan rapproché, de la tête à la poitrine, caméra en contre-plongée, en dessous, qui rend le personnage imposant. Décor : show-room de supercars en marbre noir et doré, supercars fictives alignées sous des spots, immense écran au mur avec le slogan « PRESTIGE DELMAS – N°1 DE LA RÉGION », bureau en verre au fond. Lumière : néons froids avec touches de couleur. Christophe, taureau noir massif de 52 ans, cornes polies et brillantes, anneau doré au museau, grosse chevalière en or à la main droite, costume trois pièces bordeaux sur mesure, cravate dorée, montre en or : debout devant l'écran géant, téléphone à l'oreille, tourne lentement sa chevalière, souffle par les naseaux. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Aucun texte, aucun sous-titre, aucune bulle, aucun logo.
```

**Vidéo 7** (Grok, durée 6 s)

```
Vidéo verticale 9:16 de 6 secondes à partir de l'image jointe. Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-3s] Christophe tourne sa chevalière en écoutant, le visage se ferme. Caméra : panoramique qui passe d'un personnage à l'autre. Bruitage : musique lounge.
[0.2-2.0s] DYLAN (hors champ) (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, au téléphone, soulagé) dit en français : « Papa, c'est fait. Elle est écrasée. »
[2.2-3.8s] CHRISTOPHE (voix d'homme de 52 ans, très grave, lente, calme qui fait peur, très calme, menaçant) dit en français : « Et la caméra de bord ? »
[3-6s] Il s'arrête net, naseaux qui fument. Caméra : zoom éclair sur le visage au moment de la réplique-choc. Bruitage : souffle grave.
[4.0-5.8s] DYLAN (hors champ) (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, au téléphone, la voix qui tremble) dit en français : « Quelle caméra ? »
Ambiance sonore : musique lounge, pas sur le marbre, climatisation, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 8 · 6 s · developpement · L'atelier caché de Lucas · GP

Répliques : Michel : « Avec ça, on garde la casse. On garde tout. » / Lucas : « Tu as vendu Jade, papy. » / Michel : « J'ai sauvé ce qui restait. »

**Image 8 début** (ChatGPT)

```
Image 8 : gros plan sur le visage et le haut des épaules, cadre légèrement penché pour le malaise. Décor : hangar-atelier en tôle au fond de la casse, établi couvert d'outils, lampes baladeuses pendues au plafond, pièces de moteur rangées au millimètre, vieux canapé troué, une voiture cachée sous une grande bâche grise. Lumière : nuit, une seule lampe chaude, fortes ombres. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : assis sur le vieux canapé, mallette sur les genoux, yeux humides. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : debout face à lui, lunettes de soudeur remontées, furieux. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Aucun texte, aucun sous-titre, aucune bulle, aucun logo.
```

**Vidéo 8** (Grok, durée 6 s)

```
Vidéo verticale 9:16 de 6 secondes à partir de l'image jointe. Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-3s] Michel pose la mallette sur l'établi d'une main tremblante. Caméra : caméra qui tourne lentement autour du personnage. Bruitage : clic de serrure.
[0.2-2.4s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, bas, honteux) dit en français : « Avec ça, on garde la casse. On garde tout. »
[2.6-4.0s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, rage contenue) dit en français : « Tu as vendu Jade, papy. »
[3-6s] Lucas frappe l'établi du plat de la patte. Caméra : caméra fixe avec une secousse brève au moment de l'impact. Bruitage : outils qui sautent.
[4.2-5.9s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, se lève, blessé) dit en français : « J'ai sauvé ce qui restait. »
Ambiance sonore : néon qui grésille, goutte d'huile, radio lointaine, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 9 · 10 s · retournement · L'atelier caché de Lucas · PA

Répliques : Lucas : « Tu veux un secret, papy ? » / Michel : « Quoi encore ? » / Lucas : « Dylan a payé pour une épave. » / Michel : « C'est… c'est la vraie ?! » / Lucas : « J'ai changé les plaques cette nuit. »

**Image 9 début** (ChatGPT)

```
Image 9 : plan américain, de la tête aux genoux, caméra en contre-plongée, en dessous, qui rend le personnage imposant. Décor : hangar-atelier en tôle au fond de la casse, établi couvert d'outils, lampes baladeuses pendues au plafond, pièces de moteur rangées au millimètre, vieux canapé troué, une voiture cachée sous une grande bâche grise. Lumière : nuit, une seule lampe chaude, fortes ombres. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : tient le coin d'une grande bâche grise, sourire en coin vers la caméra. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : se retourne, intrigué, sourcils froncés. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Seul texte visible, écrit lisiblement et sans faute dans le décor : sur l'établi, une plaque d'immatriculation dévissée marquée « ÉPAVE N°47 ». Aucun sous-titre, aucune bulle, aucun vrai logo.
```

**Image 9 fin** (ChatGPT)

```
Image 9 FIN (dernière image du plan, quelques secondes plus tard) : plan d'ensemble qui montre tout le décor et les personnages en pied, caméra en contre-plongée, en dessous, qui rend le personnage imposant. Décor : hangar-atelier en tôle au fond de la casse, établi couvert d'outils, lampes baladeuses pendues au plafond, pièces de moteur rangées au millimètre, vieux canapé troué, une voiture cachée sous une grande bâche grise. Lumière : nuit, une seule lampe chaude, fortes ombres. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : bouche bée, cure-dent qui tombe, pattes sur la casquette. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : appuyé sur la Falco, bras croisés, fier. Sous la bâche tombée, la vraie Falco GT orange, capot enfoncé, intacte sous les lampes. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Seul texte visible, écrit lisiblement et sans faute dans le décor : sur l'établi, une plaque d'immatriculation dévissée marquée « ÉPAVE N°47 ». Aucun sous-titre, aucune bulle, aucun vrai logo.
```

**Vidéo 9** (Grok, durée 10 s)

```
Vidéo verticale 9:16 de 10 secondes à partir de l'image jointe (l'image de fin jointe est la dernière image à atteindre). Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-2s] Lucas attrape la bâche. Caméra : travelling arrière qui révèle le décor. Bruitage : froissement.
[0.2-1.8s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, malicieux, à voix basse) dit en français : « Tu veux un secret, papy ? »
[2-4s] Il tire d'un coup sec, la bâche s'envole. Caméra : ralenti dramatique d'une seconde puis reprise à vitesse normale. Bruitage : whoosh.
[2.0-3.0s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, bougon) dit en français : « Quoi encore ? »
[3.8-5.6s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, sourire en coin) dit en français : « Dylan a payé pour une épave. »
[4-7s] La Falco orange apparaît sous les lampes, Michel recule d'un pas. Caméra : zoom éclair sur le visage au moment de la réplique-choc. Bruitage : note épique.
[5.8-7.2s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, souffle coupé) dit en français : « C'est… c'est la vraie ?! »
[7-10s] Lucas jette la plaque « ÉPAVE N°47 » sur l'établi. Bruitage : clang métallique.
[7.5-9.6s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, fier, calme) dit en français : « J'ai changé les plaques cette nuit. »
Ambiance sonore : néon qui grésille, goutte d'huile, radio lointaine, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 10 · 10 s · developpement · Le snack « Chez Nathalie » · AMORCE

Répliques : Dylan : « T'as ramassé quoi sous la presse ? » / Lucas : « Des miettes de ta voiture. » / Nathalie : « OH ! » / Dylan : « Course samedi. Tu perds, la casse est à mon père. » / Lucas : « Et si je gagne ? » / Dylan : « T'as même plus de voiture. »

**Image 10 début** (ChatGPT)

```
Image 10 : plan par-dessus l'épaule d'un personnage flou au premier plan, vers celui qui parle, caméra à hauteur des yeux. Décor : petit snack de bord de route en face de la casse, comptoir en formica rouge, néons roses, menu lumineux de frites et kebabs aux prix fictifs, tabourets chromés, figurants animaux qui mangent, vitre qui donne sur l'enseigne de la casse. Lumière : néons froids avec touches de couleur. Dylan, lévrier afghan de 21 ans au long pelage doré brushé comme une coiffure de star, museau fin relevé, lunettes de soleil miroir, grosse chaîne en or, veste en cuir blanc immaculé, tee-shirt noir, jean clair, baskets blanches de luxe : penché au-dessus du comptoir, essuie sa veste, lunettes baissées, menaçant. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : assis sur un tabouret, mange une frite, impassible. Nathalie, pie de 47 ans au plumage noir et blanc à reflets bleus, gros bigoudis roses sur la tête, longues boucles d'oreilles en plastique, téléphone toujours à la main, tablier à grosses fleurs jaunes sur un pull violet, chaussons fourrés : derrière le comptoir, téléphone levé, filme. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Aucun texte, aucun sous-titre, aucune bulle, aucun logo.
```

**Image 10 fin** (ChatGPT)

```
Image 10 FIN (dernière image du plan, quelques secondes plus tard) : plan rapproché, de la tête à la poitrine, caméra à hauteur des yeux. Décor : petit snack de bord de route en face de la casse, comptoir en formica rouge, néons roses, menu lumineux de frites et kebabs aux prix fictifs, tabourets chromés, figurants animaux qui mangent, vitre qui donne sur l'enseigne de la casse. Lumière : néons froids avec touches de couleur. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : sourire en coin vers la caméra, clé de 12 qui tourne. Dylan, lévrier afghan de 21 ans au long pelage doré brushé comme une coiffure de star, museau fin relevé, lunettes de soleil miroir, grosse chaîne en or, veste en cuir blanc immaculé, tee-shirt noir, jean clair, baskets blanches de luxe : claque la paume sur le comptoir, frites qui volent. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Aucun texte, aucun sous-titre, aucune bulle, aucun logo.
```

**Vidéo 10** (Grok, durée 10 s)

```
Vidéo verticale 9:16 de 10 secondes à partir de l'image jointe (l'image de fin jointe est la dernière image à atteindre). Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-3s] Dylan entre et se plante au-dessus de Lucas. Caméra : panoramique filé ultra rapide (whip pan) qui claque vers le personnage suivant. Bruitage : porte du snack qui claque.
[0.2-1.9s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, sifflé entre les dents) dit en français : « T'as ramassé quoi sous la presse ? »
[2.0-3.3s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, en mâchant une frite) dit en français : « Des miettes de ta voiture. »
[3-5s] Nathalie lève son téléphone. Caméra : zoom éclair sur le visage au moment de la réplique-choc. Bruitage : friteuse qui crépite.
[3.5-4.1s] NATHALIE (voix de femme de 47 ans, aiguë et rapide, adore les potins, aigu) dit en français : « OH ! »
[4.4-7.0s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, glacial) dit en français : « Course samedi. Tu perds, la casse est à mon père. »
[5-8s] Dylan pointe Lucas du doigt, nez à nez. Bruitage : silence tendu puis note grave.
[7.2-8.4s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, calme) dit en français : « Et si je gagne ? »
[8-10s] Dylan claque le comptoir, les frites volent. Caméra : secousse cartoon de la caméra à l'impact. Bruitage : claquement.
[8.5-9.8s] DYLAN (voix de jeune homme de 21 ans, traînante et méprisante, rire nasal, rire nasal) dit en français : « T'as même plus de voiture. »
Ambiance sonore : friteuse qui crépite, vieux juke-box, conversations, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 11 · 6 s · climax · L'atelier caché de Lucas · PR

Répliques : Lucas : « Ce qui est cassé, on l'écrase ? » / Michel : « Tu vas faire quoi ? » / Lucas : « Ce qui est cassé, je le répare. Samedi, elle roule. »

**Image 11 début** (ChatGPT)

```
Image 11 : plan rapproché, de la tête à la poitrine, caméra en contre-plongée, en dessous, qui rend le personnage imposant. Décor : hangar-atelier en tôle au fond de la casse, établi couvert d'outils, lampes baladeuses pendues au plafond, pièces de moteur rangées au millimètre, vieux canapé troué, une voiture cachée sous une grande bâche grise. Lumière : nuit, une seule lampe chaude, fortes ombres. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : debout devant la Falco cabossée, remonte ses lunettes de soudeur, regard de tueur. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : à côté de lui, lui tend une clé à molette. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Aucun texte, aucun sous-titre, aucune bulle, aucun logo.
```

**Vidéo 11** (Grok, durée 6 s)

```
Vidéo verticale 9:16 de 6 secondes à partir de l'image jointe. Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-3s] Lucas prend la clé à molette des pattes de Michel. Caméra : caméra qui tourne lentement autour du personnage. Bruitage : clang métallique.
[0.2-2.1s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, imite Dylan, ironique) dit en français : « Ce qui est cassé, on l'écrase ? »
[2.3-3.5s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, bougon, ému) dit en français : « Tu vas faire quoi ? »
[3-6s] Il allume la lampe baladeuse au-dessus du moteur. Caméra : zoom éclair sur le visage au moment de la réplique-choc. Bruitage : étincelles de soudure.
[3.6-6.0s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, glacial, regard caméra) dit en français : « Ce qui est cassé, je le répare. Samedi, elle roule. »
Ambiance sonore : néon qui grésille, goutte d'huile, radio lointaine, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

### Plan 12 · 6 s · cliff · L'atelier caché de Lucas · INSERT

Répliques : Michel : « On voit Dylan ? » / Lucas : « Dylan est à droite. Passager. » / Lucas : « Alors qui conduisait… ? »

**Image 12 début** (ChatGPT)

```
Image 12 : très gros plan sur un objet ou une main, caméra à hauteur des yeux. Décor : hangar-atelier en tôle au fond de la casse, établi couvert d'outils, lampes baladeuses pendues au plafond, pièces de moteur rangées au millimètre, vieux canapé troué, une voiture cachée sous une grande bâche grise. Lumière : obscurité seulement éclairée par la lueur bleue d'un écran. Lucas, raton laveur de 19 ans au pelage gris argenté, masque noir autour des yeux ambrés, queue rayée noir et gris, lunettes de soudeur relevées sur le front, traces de cambouis sur les joues, salopette orange vif tachée de cambouis, tee-shirt noir, grosse clé à molette accrochée à la ceinture : visage éclairé par l'écran d'un vieil ordinateur, la carte mémoire enfoncée dedans, yeux qui s'écarquillent. Michel, vieil ours brun massif de 68 ans, barbe grise broussailleuse, casquette de mécano bleue usée, cure-dent au coin de la bouche, gros ventre, salopette bleue délavée rapiécée aux genoux, chemise à carreaux rouge aux manches retroussées : penché par-dessus son épaule, cure-dent figé. Sur l'écran, la vidéo de la caméra de bord en noir et blanc : Dylan assis côté passager, et sur le volant une grosse patte noire avec une chevalière en or. STYLE : Animation 3D cartoon stylisée façon long-métrage d'animation premium (pas photoréaliste) : animaux anthropomorphes aux proportions cartoon, tête un peu grosse, grands yeux brillants et expressifs, sourcils très mobiles, expressions et poses exagérées, fourrure douce stylisée, vêtements stylisés. Couleurs saturées et chaudes, néons orange et lumière dorée, contre-jours dramatiques à travers la poussière. Décors riches de France d'aujourd'hui : casse automobile géante pleine de carcasses empilées, show-room de supercars en marbre, snack de bord de route, chambre d'hôpital, remplis de figurants animaux. Qualité : image clé de long-métrage d'animation 3D cartoon haut de gamme, proportions cartoon (tête un peu grosse, grands yeux brillants, sourcils très mobiles), expressions EXAGÉRÉES lisibles en une demi-seconde sur un téléphone, poses dynamiques avec de l'élan, couleurs saturées et chaudes, contre-jour et lumière dorée dramatique, profondeur de champ, décor riche plein de figurants animaux. Mêmes personnages, mêmes visages, mêmes couleurs et mêmes accessoires que les portraits de référence et les images précédentes. Format vertical 9:16. Aucun texte, aucun sous-titre, aucune bulle, aucun logo.
```

**Vidéo 12** (Grok, durée 6 s)

```
Vidéo verticale 9:16 de 6 secondes à partir de l'image jointe. Animation 3D cartoon, rythme très nerveux, aucun temps mort.
[0-3s] La vidéo de la caméra de bord démarre à l'écran. Caméra : zoom rapide et court sur le visage au moment de la révélation (une seule fois par épisode maximum). Bruitage : bip de lecture.
[0.2-1.4s] MICHEL (voix d'homme de 68 ans, rocailleuse et lente, accent du sud-ouest, pressé, à voix basse) dit en français : « On voit Dylan ? »
[1.6-3.6s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, lent, incrédule) dit en français : « Dylan est à droite. Passager. »
[3-6s] L'image se fige sur la patte au volant, coupure noire. Bruitage : coupure sèche.
[3.8-5.8s] LUCAS (voix de jeune homme de 19 ans, grave et calme, phrases courtes, pointe d'ironie, souffle coupé) dit en français : « Alors qui conduisait… ? »
Ambiance sonore : néon qui grésille, goutte d'huile, radio lointaine, bruitages cartoon bien appuyés (whoosh, impacts, chocs).
Règles : animation 3D cartoon identique à l'image (mêmes personnages, mêmes couleurs, même décor), mouvements rapides et pleins d'énergie avec des réactions exagérées façon dessin animé, lèvres synchronisées en français, seul celui qui parle bouge les lèvres, aucune déformation du visage ni des mains, aucun sous-titre ni texte ajouté, aucune musique.
```

## 3. Publication

Titre de couverture : Ils l'ont payé 100 000 € pour l'écraser 😳

```
La voiture qui a renversé sa sœur arrive dans sa casse… pour être détruite. Partie 1. Qui conduisait, d'après toi ?

#partie1 #histoire #voiture #animaux #ia #drama
```

Commentaire épinglé :

```
Qui conduisait la Falco ? 🐂 Le père de Dylan / 🐕 Dylan ment, c'était lui
```

Hooks de rechange (si moins de 2 000 vues en 2 h, refaire seulement le plan 1) :

- Ils m'ont payé 100 000 € pour écraser cette voiture.
- Cette voiture a renversé ma sœur. Mon grand-père l'a vendue.
- Le chauffard a déposé sa voiture chez moi. Pour la détruire.