# Ignored Requirements

Les éléments suivants apparaissent dans le document de cadrage initial mais ne
sont plus applicables au projet actuel.

## Paiement et commercialisation

Ignorer :

- paiement 5 €
- accès premium
- page premium
- Stripe
- tunnel commercial
- souscription
- objectif de conversion
- offre payante et déblocage de prédictions
- indicateurs liés à l'achat ou à la demande de premium

Raison :

Le projet est désormais un prototype personnel non commercial, partagé avec des
amis. Les mentions premium doivent être reformulées en mode privé, accès amis ou
partage privé.

## Stack frontend

Ignorer :

- Next.js
- React

Raison :

Le frontend final doit être réalisé avec Angular. Le moteur de prédiction reste
hors d'Angular.

## Scalabilité

Ignorer :

- architecture SaaS
- comptes utilisateurs complexes
- infrastructure scalable
- automatisation trop avancée
- microservices
- optimisation prématurée
- déploiement avancé

Raison :

Le projet est personnel. La simplicité, la lisibilité et un flux
`script métier -> JSON -> Angular` priment.

## Paris sportifs

Conserver uniquement :

- la déduction statistique de marchés depuis la matrice
- la comparaison transparente entre probabilités et résultats réels

Ignorer :

- incitation au pari
- promesse de gain
- intégration bookmaker
- logique de mise
- gestion de bankroll
- stratégie Kelly
- recherche de cotes ou de value commerciale

Raison :

Le projet doit rester un outil d'analyse probabiliste et de simulation. Les
anciens scripts de paris présents dans `drc-prototype` et `drc-nba` ne sont pas
des exigences du nouveau produit.

## Comptes et accès

Ignorer :

- comptes utilisateurs
- abonnement
- rôles complexes
- authentification orientée produit commercial

Raison :

Un éventuel accès privé léger peut être ajouté plus tard, mais il n'est pas
nécessaire pour la première version locale partagée avec des amis.

## Fonctionnalités hors première version

Ignorer pour le démarrage :

- application mobile native
- modèle live complexe minute par minute
- marchés joueurs, mi-temps, handicaps et combinés avancés
- collecte multi-fournisseurs
- refonte totale des briques extraites

Raison :

La première version utile doit valider la chaîne existante, les contrats JSON,
le détail d'un match, la matrice, les marchés et l'historique.
