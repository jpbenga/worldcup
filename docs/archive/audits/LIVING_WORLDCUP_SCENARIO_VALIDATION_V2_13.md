# Living World Cup Scenario Validation V2.13

La validation technique V2.13 est **PASS**.

Le validateur confirme l'existence du scénario vivant et des parcours
représentatifs, la présence d'un vainqueur projeté, d'une finale projetée, des
cinq tours à élimination directe et de la petite finale. Il confirme également
les `72` matchs connus, la cible de `104` matchs et les `32` slots projetés.

Le champ `official_bracket_available` est présent et vaut `false` dans le
snapshot actuel. Les limitations sont donc obligatoires et décrivent le
bracket comme un scénario dérivé des simulations. La variante expérimentale
reste `experimental_lab_only_not_promoted`.

Les fichiers protégés de prédictions, résultats moteur et résumé Optuna sont
comparés avec Git. Ils restent inchangés. Le validateur vérifie aussi que les
valeurs numériques sont finies et qu'aucune signature de secret n'apparaît
dans les nouveaux agrégats.

Aucun réentraînement et aucune relance Optuna ne font partie de V2.13. Le build
Angular et les tests Angular passent avec Node 22.22.3. Aucun fichier interdit
ou supérieur à 10 Mo n'est suivi ou produit, et le contrôle de sécurité ne
révèle aucune valeur secrète.
