# Data Freshness Status V2.17

Le statut de fraîcheur est construit sans modifier les résultats :

```bash
python3 backend/scripts/build_data_freshness_status_v2_17.py
```

Il utilise le dernier manifest Matchday disponible et le résumé des résultats existants. Il publie la date du dernier refresh, son âge, le nombre de résultats officiels intégrés, les matchs live et à venir, ainsi que les noms des moteurs officiels. Une fraîcheur n’est jamais inventée : le statut devient `unknown` lorsque la date manque et `stale` lorsque le dernier refresh dépasse douze heures.

Au moment de V2.17, le dernier refresh détecté est ancien et doit donc produire un avertissement opérateur. Aucun indicateur n’est ajouté à l’interface dans cette itération, car des assets frontend Matchday sont déjà modifiés localement hors scope; le JSON frontend est prêt pour une intégration ultérieure contrôlée.
