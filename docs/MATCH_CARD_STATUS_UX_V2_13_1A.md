# Match Card Status UX V2.13.1A

Les cards de groupes conservent une densité faible et changent d'ambiance
selon le statut du match. Un match à venir utilise un fond bleu sombre et
affiche l'horaire, le Prono SimuAI, le favori et la confiance. Le score central
reste `vs` afin de ne pas faire passer le prono pour un résultat réel.

Un match en direct utilise un accent ambre, affiche le score live au centre et
rappelle le Prono SimuAI initial. Le texte En direct évite de dépendre
uniquement de la couleur.

Un match terminé affiche le score officiel au centre. La surface devient verte
si le score exact est trouvé, cyan pour une réussite partielle et rouge si le
prono est raté. Un texte résume en parallèle Score exact, Bon résultat score
différent, Score dans la sélection ou Prono raté.

La navigation par journées et le classement visible sont conservés. Les cards
restent des points d'entrée vers la modal détaillée.
