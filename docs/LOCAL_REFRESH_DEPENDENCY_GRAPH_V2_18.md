# Local Refresh Dependency Graph V2.18

La chaîne locale suit cet ordre : résultats API-Football vers cache officiel, évaluation des prédictions, historique, scoreboard, timeline, standings live, vue d’état des matchs, SimuAI Tournament Engine V3, scénario représentatif, moteur et view model Road to the Trophy, statut de fraîcheur, assets frontend et validation.

Le pipeline Matchday V2.10 couvre résultats, évaluation, standings et vues dépendantes historiques. Les scripts V2.12 reconstruisent `prediction_history_v2_12.json`, `model_scoreboard_v2_12.json` et `prediction_performance_timeline_v2_12.json`. Le rebuild V3 produit la simulation complète et le scénario représentatif, puis la promotion V2.15 republie `road_to_the_trophy_engine.json`.

Les sources sont les caches raw, résultats officiels, prédictions pré-match gelées et ratings. Les sorties generated sont copiées vers snapshots et, lorsqu’elles alimentent Angular, vers frontend assets. Une étape est sautée uniquement si le détecteur confirme qu’aucun résultat, asset, nombre de simulations, version ou validation ne l’exige.
