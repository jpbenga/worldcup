# Prototype Prediction Engine Status

## Positionnement

Le moteur actuel est le **Prototype Prediction Engine**. Il permet de terminer
le workflow produit complet avec une architecture simple et remplaçable.

Il calcule :

- des expected goals à partir d'entrées simples ;
- une matrice de scores Poisson/Dixon-Coles ;
- des marchés dérivés ;
- une variante Elo expérimentale et une comparaison avec le baseline.

## Limites explicites

Le moteur n'est pas entraîné ni calibré sur des compétitions historiques. Il
ne démontre pas encore une qualité prédictive suffisante pour être présenté
comme un modèle robuste. Avec les fixtures API-Football futures, ses entrées
baseline sont neutres et clairement documentées comme non calibrées.

L'audit V0.5.1 confirme que le score modal baseline est `1-1` pour les `72`
fixtures, et que la variante Elo ne change aucun de ces scores modaux. Cette
uniformité vient des xG neutres `1.35 / 1.35`, pas d'un bug de tri ou d'une
absence de ratings Elo. Elle est affichée dans l'interface et ne doit pas être
masquée par une diversification artificielle.

Il ne réalise ni simulation de tournoi, ni apprentissage historique, ni
backtesting sur des matchs sans résultat.

## Stratégie

L'image produit est volontairement simple : **moteur 2 chevaux maintenant,
Rolls Royce plus tard**. Professionnellement, cela signifie :

> The current engine is intentionally simple and replaceable.

Nous conservons ce moteur pour construire et valider l'acquisition, la
normalisation, la provenance, les snapshots et l'interface. Une future version
pourra remplacer ses fonctions internes par un moteur historiquement calibré
sans changer le contrat général du pipeline.

Voir `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` pour les mesures et la décision.

## V0.6 — Discovery et trajectoire

V0.6 confirme que les briques nettoyées de l'ancien moteur sont présentes,
mais qu'aucun modèle entraîné fiable ni jeu de paramètres historiques validé
n'est récupérable tel quel. Le moteur prototype reste donc inchangé.

La trajectoire retenue est de préserver les contrats JSON, puis d'acquérir un
historique international chronologique avant de reconstruire un
Poisson/Dixon-Coles calibré. Voir `docs/CURRENT_ENGINE_AUDIT.md`,
`docs/HISTORICAL_DATA_STRATEGY.md` et `docs/FUTURE_ENGINE_BLUEPRINT.md`.
