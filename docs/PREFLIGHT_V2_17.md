# Preflight V2.17

Le preflight non destructif doit être exécuté avant commit ou push :

```bash
python3 backend/scripts/preflight_v2_17.py
```

Il vérifie que le doctor est acceptable, que les fichiers critiques et la validation documentaire existent, que les prédictions actives et le moteur Road to the Trophy ne présentent aucun diff, qu’aucun fichier interdit n’est suivi, qu’aucun gros fichier inattendu n’est présent et que la clé API n’est jamais imprimée. Il liste également l’état Git complet.

Les changements frontend détectés produisent une demande explicite de build et de tests. Un worktree sale préexistant reste un avertissement plutôt qu’un blocage, car l’opérateur doit pouvoir contrôler un refresh local sans masquer son existence. Les changements sur les fichiers protégés, eux, bloquent le preflight.
