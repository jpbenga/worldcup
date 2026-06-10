# SimuMondial 2026 Frontend

Application Angular 22 et Tailwind CSS qui affiche les snapshots générés par le
pipeline backend.

```bash
nvm use
npm install
npm start
```

Build et tests :

```bash
npm run build
npm test -- --watch=false
```

Les fichiers JSON affichés se trouvent dans `src/assets/data/`. Pour les
actualiser, régénérer les données depuis la racine du dépôt puis recopier les
trois snapshots comme indiqué dans `../docs/ANGULAR_FRONTEND_NOTES.md`.
