# Start Local App V2.18

La commande locale principale est :

```bash
python3 backend/scripts/start_local_app_v2_18.py --auto-refresh --fetch --simulations 50000
```

Elle lance le doctor, vérifie si un refresh est nécessaire, exécute l’orchestrateur uniquement lorsque la décision l’exige, reconstruit le statut de fraîcheur puis démarre Angular. `--no-fetch` interdit l’appel API et utilise les caches locaux. `--force-refresh` reconstruit toute la chaîne. `--no-refresh` lance seulement l’application et `--no-start` prépare les données sans ouvrir le serveur frontend.

Le lancement reste strictement local. La clé API reste côté Python et n’est jamais transmise au navigateur. Si npm, le frontend ou un script requis manque, la commande échoue avec un message explicite. Les refreshs inutiles et la simulation lourde sont sautés lorsque la cohérence est déjà démontrée.
