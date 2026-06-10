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
