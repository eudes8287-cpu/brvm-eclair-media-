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
