# Analyse — Accessibilité scolaire dans la préfecture de Zio

## Constats principaux

L'analyse de l'accessibilité scolaire dans la préfecture de Zio révèle des disparités significatives selon le niveau d'enseignement :

*   **Enseignement Primaire** : La desserte est globalement excellente et homogène. La distance moyenne pondérée est de **1,3 km**, avec une densité d'établissements (533 écoles) qui couvre bien le territoire. Même les cantons ruraux restent souvent en dessous de 2-3 km.
*   **Collèges et Lycées** : Les distances augmentent fortement. Pour les lycées, la distance moyenne bondit à **4,2 km**.
*   **Cantons les moins bien desservis** : 
    *   Les cantons de **Gbatopé, Gblainvié, gapé-kpodji et Gamé-séva** et les zones périphériques de **Kovié** présentent les distances moyennes les plus élevées pour les lycées (souvent > 5 km).
    *   Les communes urbaines comme **Zio 1 (Tsévié)** bénéficient d'une proximité immédiate (< 1 km), tandis que les zones rurales de **Zio 4** sont les plus pénalisées par l'éloignement des structures de second cycle.

## Limites méthodologiques

*   **Données de population** : L'utilisation d'une source désagrégée statistiquement (Meta 30m) peut surestimer la population dans des zones de brousse ou sous-estimer la micro-densité villageoise réelle.
*   **Hypothèse démographique** : L'application d'un ratio fixe (14%, 12%, 10%) ne tient pas compte des variations locales de fécondité ou de migration entre cantons urbains et ruraux.
*   **Distance euclidienne** : Le calcul en "vol d'oiseau" (via UTM 31N) ne reflète pas la pénibilité du trajet réel (chemins, barrières géographiques comme les cours d'eau, état des routes).

## Recommandations

Pour améliorer l'équité territoriale, je recommande :
1.  **Implantation d'un nouveau Lycée dans le canton de Gapé-Centre** ou ses environs immédiats pour réduire la barrière des 5-7 km qui peut favoriser le décrochage scolaire.
2.  **Renforcement des capacités d'accueil** dans les collèges de **Kovié** qui servent de pivots pour une large population rurale.
3.  Utiliser une analyse de **réseau routier (Network Analysis)** pour une phase 2 afin d'affiner les temps de trajet réels.
