# Operator Doctor V2.17

Le doctor opérateur fournit un diagnostic rapide avant de travailler :

```bash
python3 backend/scripts/operator_doctor_v2_17.py
```

Il affiche des statuts simples pour l’environnement, les données critiques, Road to the Trophy, le dernier refresh et Git. Son rapport JSON conserve les versions détectées, les fichiers présents, les avertissements et la commande suivante recommandée. La présence d’une clé API est représentée uniquement par un booléen; sa valeur n’est jamais imprimée.

Un worktree sale produit un avertissement afin de ne pas confondre les refreshs locaux existants avec le travail de l’itération courante. Un fichier critique ou un runtime absent produit un échec. Le doctor ne modifie aucun moteur, aucune prédiction et aucun résultat.
