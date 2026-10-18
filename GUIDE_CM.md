# Guide créatif BRVM Éclair (à lire avant de créer un visuel ou une vidéo)
Public : débutants complets. Langage simple, zéro jargon sans explication. Chaque visuel : définition courte + « EN CLAIR » + « À RETENIR ».
## Règles fixées par le propriétaire (Eudes)
- PAS DE DATE sur les contenus (mots du jour, quiz, vrai/faux, pédagogie) : ils doivent rester réutilisables. Les dates ne figurent que sur les bulletins de clôture (date de la SÉANCE du BOC) et le récap hebdo.
- Mention légale exacte partout (visuels, vidéos, textes) : « Ceci est une information, pas un conseil en investissement ». (constante DISCLAIMER dans scripts/common.py ; dans les textes de posts : ⚠️ Ceci est une information, pas un conseil en investissement.)
- VARIÉTÉ obligatoire des créas, avec points de repère de charte : éclair + « BRVM ÉCLAIR » en haut à gauche, police Inter, pastille de rubrique, blocs EN CLAIR / À RETENIR, accent orange (ou jaune sur fond vert/sarcelle), mention légale en bas à droite.
- Voix : ff_siwis (Kokoro) ; chiffres, sigles et « % » sont normalisés automatiquement (make_voice.normalize). Écrire les phrases voix comme on parle, courtes, avec virgules pour les respirations.
## Variété (make_card.py)
- theme : navy, orange, light, teal, sand, violet, emerald, wine
- layout : standard, bignumber, qa, steps, versus, poster
- format : square (1080x1080) ou portrait (1080x1350) ; deco : bolt, rings, dots, diag, none
- Ne jamais enchaîner deux visuels avec le même couple thème+layout ; alterner carré/portrait. Lister visuels/ avant de choisir.
- Vidéos (make_video.py) : champ "theme" (navy, teal, violet, emerald, wine) ; contenu différent de Facebook le même jour (accroche en 2 s, 20 à 35 s).
## Faits vérifiés utilisables
- BRVM : 48 sociétés cotées, capitalisation actions > 21 400 Mds FCFA (9/10/2026), créée en 1998, Bourse des 8 pays de l'UEMOA (à ne pas figer sur les contenus réutilisables).
## Interdits
IRVM (sauf post dédié validé), conseil d'investissement, prévision de cours, chiffre non vérifié, mention de l'employeur du propriétaire.
