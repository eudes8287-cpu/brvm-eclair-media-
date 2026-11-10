# Synthèse (TikTok @eudes9972) — procédure de production quotidienne

Propriétaire : Eudes. Objectif : audience puis monétisation. Aucun contenu copié : tout est original (voix de synthèse, cartes libres, musique synthétisée).

## Règles absolues
1. **Metricool, marque « BRVM Éclair » (blogId 7633075)** : le réseau `tiktok` = Synthèse (@eudes9972). Le réseau `facebook` de cette marque = page BRVM Éclair. Pour Synthèse, n'utiliser QUE `{"network":"tiktok"}`. Ne jamais envoyer un contenu BRVM sur `tiktok` ni un contenu Synthèse sur `facebook`.
2. Chaque chiffre ou fait est vérifié sur 2 sources indépendantes (WebSearch puis WebFetch de la page). Si deux sources divergent, ne pas utiliser le chiffre. Aucune population, date ou record non vérifié.
3. Sujets sensibles interdits : conseils médicaux ou de santé, personnalités vivantes (accusations, vie privée), politique partisane, pronostics, finance.
4. Toujours déclarer le contenu généré par IA : `tiktokData.isAigc = true`.
5. Ne jamais télécharger ni republier la vidéo d'un autre compte. Visuels = cartes Natural Earth (`data/countries-50m.json`) et éléments dessinés en code.
6. Lire `LOG.md` avant de choisir un sujet : ne jamais refaire un sujet déjà publié.

## Étapes
1. Choisir dans `PLAN.md` le prochain sujet non fait (colonne Statut vide) dont le format est disponible dans le moteur.
2. Vérifier les faits (règle 2) et noter les sources dans `LOG.md`.
3. Écrire `specs/NNN_nom.json` (modèle : `specs/001_plus_petit_pays.json`). Scènes disponibles : `hook`, `reveal` (zoom carte + repère), `stat` (compteur), `compare` (grille d'icônes), `outro`. Durée visée : 18 à 28 s. Voix en français : texte écrit comme on le prononce (« zéro virgule quarante-quatre », pas « 0,44 »), champ `caption` pour l'affichage.
4. Rendre : `python3 -I synthese/scripts/synthese_video.py synthese/specs/NNN_nom.json synthese/videos/NNN_nom.mp4` (environ 75 s). Les images de contrôle sont créées à côté (`*.f*.png`) : les regarder, puis les supprimer avant le commit.
5. Contrôler : ffprobe (1080x1920, h264+aac), volume moyen proche de -16 dB, aucun texte hors cadre ni coupé, sous-titres hors des 350 px du bas.
6. `git fetch origin main`, rebaser, ajouter, commit, push sur `main`. URL publique : `https://raw.githubusercontent.com/eudes8287-cpu/brvm-eclair-media-/main/synthese/videos/NNN_nom.mp4`.
7. Programmer via Metricool `createScheduledPost` : blogId 7633075, `providers:[{"network":"tiktok"}]`, fuseau `Africa/Abidjan`, `media:[URL]`, `tiktokData:{"privacyOption":"PUBLIC_TO_EVERYONE","isAigc":true,"title":"…"}`, légende courte avec accroche + 4 à 6 hashtags. Créneaux conseillés (statistiques Metricool, heure d'Abidjan) : 10 h et 18 h en semaine, 10 h et 12 h le week-end. Ne pas programmer deux vidéos à moins de 6 h d'écart.
8. Si Metricool refuse (quota, erreur de réseau) : repli sur Buffer (canal « eudes9972 TikTok Account », action « Add to Queue », méthode `schedule`, pièce jointe vidéo) et le noter dans `LOG.md`.
9. Ajouter une ligne dans `LOG.md` (date, sujet, sources, URL de la vidéo, lien Metricool) et passer le sujet à « fait » dans `PLAN.md`.

## Boucle d'amélioration (chaque lundi)
Lire les statistiques TikTok via Metricool (`getAnalyticsDataByMetrics`, connecteur `posts` : TKPO07 vues, TKPO13 taux de visionnage complet, TKPO15 temps moyen, TKPO08 à TKPO10 interactions ; connecteur `evolution` : TKEV07 abonnés). Classer les vidéos par taux de visionnage complet puis par vues. Ajouter dans `LOG.md` un bilan de 5 lignes : formats gagnants, formats à abandonner, ajustement de la semaine (rythme, rubrique, accroche).
Règle de décision : après 3 vidéos d'un même format sous 300 vues chacune, réduire ce format de moitié. Un format qui dépasse 3 fois la médiane passe en priorité dans `PLAN.md`.

## Compte anglais
À partir de la 3e semaine : même moteur avec `"lang":"en"` (voix `af_heart`, à tester). Compte et canal séparés, à créer et connecter par Eudes (une seule fois).


# PROCÉDURE v2 (depuis le 10/11/2026) — format sujet unique, publication via Buffer
Remplace les étapes 3 à 8 ci-dessus pour les vidéos de type « sujet unique ». Les règles absolues restent valables (aucun Facebook, son obligatoire, 2 sources par fait, aucun contenu BRVM, sujets sensibles interdits).
1. Sujet : prochaine ligne « à faire » de la table « SEMAINE TEST » de PLAN.md pour la date du jour. Si la ligne du jour est déjà « fait », s'arrêter.
2. Faits : 6 à 8 faits sur UN sujet (singularités, secrets, histoire, actualité), chacun confirmé par 2 sources lues (WebSearch puis WebFetch). Écarter tout fait à une seule source ou aux sources divergentes. Noter les sources dans LOG.md.
3. Clips (Pixabay, libres pour usage commercial) : `orshot_search_stock_media` (type video), puis OBLIGATOIREMENT `orshot_use_stock_media` sur chaque ref, puis `curl -o clip.mp4 https://storage.orshot.com/stock/pixabay/video/ID.mp4` (vérifier avec ffprobe ; relancer si timeout). Regarder une image de chaque clip : l'image doit correspondre au fait raconté (pas de tour Eiffel pour le Louvre). Prévoir 8 à 9 segments (accroche, 6 à 7 faits, conclusion), un clip par segment, 5 à 8 s chacun.
4. Spec : copier `specs/002_paris_6_secrets.json`, champs par segment : clip, ss (début en s), fx (centre du cadrage 0..1), num, title, big (chiffre ou mot-clé affiché), voice (texte parlé : nombres écrits en toutes lettres), caption (texte affiché). Voix de 14 mots maximum par fait (environ 5 à 7 s). Phrase finale : appel au commentaire + abonnement.
5. Rendu : `python3 -I synthese/scripts/deep_dive.py spec.json synthese/videos/NNN_nom.mp4` (environ 4 à 5 min ; voix Kokoro, musique originale, sous-titres karaoké).
6. Contrôle : ffprobe (1080x1920, h264+aac), volumedetect (moyenne autour de -14 dB), silencedetect (aucun silence), 6 images à regarder (texte lisible, hors des 380 px du bas). Pas de publication sans son.
7. Dépôt : `git fetch origin main`, rebase, add, commit, push sur main. URL : `https://raw.githubusercontent.com/eudes8287-cpu/brvm-eclair-media-/main/synthese/videos/NNN_nom.mp4`.
8. Publication via **Buffer** (Metricool a atteint son quota gratuit le 10/11) : Zapier `execute_zapier_write_action`, selected_api `BufferCLIAPI`, action `update`, tool_name `buffer_add_to_queue`, params `{"method":"schedule","organizationId":"6ad18d12b6b63bd0b2f68c68","channelId":"6ad1b505778b240e2f24f41c","dynamic_properties":{"attachment":"video","scheduling_type":"direct","scheduled_at":"AAAA-MM-JJT12:00:00+00:00","text":"<légende>","video":"<URL>"}}`. Si l'heure est passée, `method` = `share_now` (sans `scheduled_at`). Le canal `6ad1b505778b240e2f24f41c` est @eudes9972 (Synthèse) ; ne JAMAIS utiliser `6ad18f13778b240e2f22de5c` (brvm.clair) ni la page Facebook. Légende : accroche + question d'engagement + 6 à 9 hashtags (#fyp #pourtoi + thème + #synthese). Buffer ne gère pas l'indicateur « contenu généré par IA ».
9. Vérification : relire les éléments envoyés (`buffer_new_sent_item`, organizationId + channelId en dynamic_properties) ; le résultat est volumineux : l'enregistrer dans un fichier et lire les 3 premiers éléments en Python. Noter le lien TikTok et les statistiques (vues, j'aime, commentaires) dans LOG.md.
10. Mise à jour : ligne du jour de PLAN.md passée à « fait », ligne ajoutée à LOG.md, commit et push.
Chaque lundi : relever via Buffer les statistiques des vidéos de la semaine (même lecture que l'étape 9), écrire un bilan de 5 lignes dans LOG.md et ajuster PLAN.md.
