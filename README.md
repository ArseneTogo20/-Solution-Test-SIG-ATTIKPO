# Test Technique SIG-01 — Accessibilité scolaire dans la préfecture de Zio

> **Programme** : PDAAP — Digitalisation des Administrations Publiques du Togo  
> **Poste** : SIG Analyst Junior  
> **Durée** : 3 heures  
> **Validation** : `uv sync && uv run pytest`

---

## Contexte

Dans le cadre du PDAAP, le Togo Data Lab souhaite produire des indicateurs géospatiaux pour le pilotage des politiques publiques. L'un des enjeux majeurs du Ministère de l'Éducation et de la Formation Professionnelle est de mesurer l'**accessibilité géographique aux établissements scolaires** sur l'ensemble du territoire.

Vous travaillez sur un cas pilote : la **préfecture de Zio** (région Maritime), qui compte environ 293 000 habitants et plus de 1 000 établissements scolaires répartis dans 16 cantons. Votre mission est de calculer la **distance moyenne d'accès à l'école la plus proche** pour la population, par catégorie d'établissement, puis d'agréger ces résultats au niveau cantonal et communal pour identifier les zones mal desservies.

---

## Sources de données

Trois fichiers GeoPackage (`.gpkg`) sont fournis dans `data/` :

### `Etablissement_scolaire_Zio.gpkg`

- **Source** : Portail GeoData de la République Togolaise
- **Format** : GeoPackage, couche `etablissements_scolaires`, géométrie Point (EPSG:4326)
- **Volume** : 1 034 établissements
- **Colonnes** :

| Colonne | Description |
|---|---|
| `prefecture_nom_bdd` | Préfecture (toujours "Zio") |
| `commune_nom_bdd` | Commune : Zio 1, Zio 2, Zio 3, Zio 4 |
| `canton_nom_bdd` | Canton (16 cantons) |
| `nom_localite` | Nom de la localité |
| `etablissement_nom` | Nom de l'établissement |
| `etablissement_categorie` | Catégorie : `Jardin (maternelle)`, `Ecole primaire`, `College`, `Lycée` |
| `ministere_tutelle` | Ministère de tutelle (MEPSTA) |
| `geometry` | Point (longitude, latitude) |

### `Population_Zio.gpkg`

- **Source** : Meta — High Resolution Population Density Maps (open data, 2020)
- **Format** : GeoPackage, couche `intersection`, géométrie MultiPoint (EPSG:4326)
- **Résolution spatiale** : ~30 mètres (grille régulière de ~0.000278°)
- **Volume** : 112 466 points
- **Colonnes** :

| Colonne | Description |
|---|---|
| `longitude` | Longitude du centroïde de la cellule |
| `latitude` | Latitude du centroïde de la cellule |
| `tgo_general_2020` | Population estimée dans la cellule (valeur continue, issue d'une désagrégation statistique) |
| `geometry` | MultiPoint |

**Note importante** : Chaque point de grille représente une estimation de population désagrégée. La valeur `tgo_general_2020` n'est pas un nombre entier de personnes mais une estimation continue (ex: 2.56). La somme sur l'ensemble de la préfecture donne ~293 000 habitants.

### `Togo_Cantons.gpkg`

- **Source** : Découpage administratif du Togo
- **Format** : GeoPackage, géométrie MultiPolygon (EPSG:4326)
- **Volume** : 396 cantons pour l'ensemble du Togo (16 pour la préfecture de Zio)
- **Colonnes utiles** :

| Colonne | Description |
|---|---|
| `region_nom` | Région (Maritime pour Zio) |
| `prefecture_nom` | Préfecture (filtrer sur "Zio") |
| `commune_nom` | Commune (Zio 1, Zio 2, Zio 3, Zio 4) |
| `canton_nom` | Nom du canton (16 cantons dans Zio) |
| `canton_id` | Identifiant unique du canton |
| `geometry` | MultiPolygon — limites géographiques du canton |

Ce fichier fournit les **polygones des limites cantonales**, nécessaires pour rattacher chaque point de population à son canton via un spatial join.

---

## Tâches

### Partie 1 — Calcul de la distance à l'école la plus proche (40% de la note)

Pour **chaque point de population**, calculer la distance (en mètres) à l'établissement scolaire le plus proche, pour les **3 catégories** suivantes :

- Distance à l'**école primaire** la plus proche
- Distance au **collège** le plus proche
- Distance au **lycée** le plus proche

**Exigences** :
- Le calcul doit être **performant** : avec 112 466 points de population et jusqu'à 533 établissements par catégorie, le candidat doit choisir et implémenter une méthode de calcul efficace. Le calcul complet doit s'exécuter en moins de **120 secondes**.
- Les distances doivent être en **mètres**. Le candidat justifie son approche (distance géodésique, projection locale, ou autre).
- Le résultat est un DataFrame avec les colonnes de population d'origine + 3 colonnes de distance ajoutées.
- Exporter le résultat dans `data/output/population_distances.parquet`.

### Partie 2 — Agrégation par canton et estimation de la population scolaire (35% de la note)

1. **Rattacher chaque point de population à son canton** via un spatial join avec les polygones de `Togo_Cantons.gpkg` (filtré sur la préfecture de Zio).

2. **Estimer la population scolaire** par catégorie en appliquant les proportions suivantes à la population de chaque point :

   | Catégorie | Part de la population totale |
   |---|---|
   | Primaire (6-11 ans) | 14% |
   | Collège (12-15 ans) | 12% |
   | Lycée (16-18 ans) | 10% |

   **⚠️ Hypothèse forte** : ces proportions sont une estimation grossière appliquée de manière homogène sur tout le territoire. Elles ne reflètent pas la réalité démographique locale, qui peut varier significativement entre zones urbaines et rurales, et selon les données de recensement réelles. De même, la distance moyenne obtenue dépend directement de la résolution spatiale de la source de population (~30m) — une résolution différente donnerait des résultats différents. Le candidat doit mentionner ces limites dans son analyse.

3. **Calculer la distance moyenne pondérée** d'accès à l'école la plus proche, par catégorie. La pondération se fait par la population scolaire estimée de chaque point :

   ```
   distance_moyenne_primaire = Σ(dist_primaire_i × pop_primaire_i) / Σ(pop_primaire_i)
   ```

   Calculer cette distance moyenne **à deux niveaux d'agrégation** :
   - **Par canton** (16 cantons)
   - **Par commune** (Zio 1, Zio 2, Zio 3, Zio 4)

4. **Compter le nombre d'établissements** de chaque catégorie par canton (en utilisant la localisation des établissements et le spatial join avec les polygones cantonaux).

5. **Exporter les résultats** :
   - `data/output/agregation_cantons.parquet` : une ligne par canton, avec population, population scolaire estimée, distances moyennes pondérées par catégorie, et nombre d'établissements par catégorie
   - `data/output/agregation_communes.parquet` : une ligne par commune + une ligne "Total"

### Partie 3 — Visualisation et analyse (25% de la note)

1. Produire **2 à 3 visualisations** (enregistrées en PNG ou HTML dans `output/viz/`) permettant d'observer :
   - Une **carte choroplèthe** des cantons colorés par la distance moyenne d'accès (par exemple pour l'école primaire)
   - Les **zones les plus mal desservies** — le candidat définit et justifie un seuil de distance
   - Au moins une visualisation **comparative** entre catégories ou entre cantons (ex: graphique en barres des distances par canton, comparaison primaire vs lycée)

2. Rédiger une **courte note d'analyse** dans `ANALYSIS.md` (15-20 lignes) :
   - Quels cantons sont les moins bien desservis et pour quelle catégorie ?
   - Y a-t-il des disparités visibles entre communes ?
   - Quelles limites méthodologiques identifiez-vous ?
   - Si vous deviez recommander l'implantation d'un nouvel établissement, où et de quel type ?

---

## Structure attendue du repo

```
sig-01-accessibilite-scolaire/
├── pyproject.toml
├── README.md                       # Ce fichier (énoncé)
├── ANALYSIS.md                     # Note d'analyse (Partie 3)
├── .gitignore
├── data/
│   ├── Etablissement_scolaire_Zio.gpkg   # Source (fourni)
│   ├── Population_Zio.gpkg               # Source (fourni)
│   ├── Togo_Cantons.gpkg                 # Source (fourni)
│   └── output/                           # Résultats (à produire)
│       └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── distance_calculation.py     # Partie 1 : calcul des distances
│   ├── aggregation.py             # Partie 2 : spatial join + agrégation cantonale/communale
│   └── visualization.py           # Partie 3 : production des cartes
├── output/
│   └── viz/                        # Visualisations (à produire)
│       └── .gitkeep
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_distances.py
    ├── test_aggregation.py
    └── test_visualization.py
```

---

## Tests fournis (`tests/`)

**`test_distances.py`** :
- Le fichier `data/output/population_distances.parquet` existe
- Il contient les colonnes `dist_primaire`, `dist_college`, `dist_lycee`
- Le nombre de lignes est 112 466
- Toutes les distances sont positives (> 0.1m)
- Les distances sont en mètres (médiane de `dist_primaire` entre 200 et 8 000)
- La médiane de `dist_primaire` < médiane de `dist_lycee`
- Aucune valeur nulle
- Le calcul complet s'exécute en moins de 120 secondes

**`test_aggregation.py`** :
- Les fichiers `data/output/agregation_cantons.parquet` et `data/output/agregation_communes.parquet` existent
- `agregation_cantons.parquet` contient 16 lignes (un par canton de Zio)
- `agregation_communes.parquet` contient au moins 5 lignes (4 communes + 1 total)
- Colonnes cantons : `canton_nom`, `commune_nom`, `population_totale`, `pop_primaire`, `pop_college`, `pop_lycee`, `dist_moy_primaire`, `dist_moy_college`, `dist_moy_lycee`, `nb_primaire`, `nb_college`, `nb_lycee`
- La somme de `population_totale` des cantons est cohérente (~293 000 ± 5%)
- `pop_primaire` ≈ 14% de `population_totale` par canton (tolérance ± 1 point)
- Les distances moyennes sont positives et réalistes
- La somme de `nb_primaire` sur les 16 cantons est 533

**`test_visualization.py`** :
- Au moins 2 fichiers dans `output/viz/`
- `ANALYSIS.md` existe et contient plus de 500 caractères

---

## Critères d'évaluation

| Critère | Poids |
|---|---|
| Calcul de distance correct et performant | 30% |
| Tests pytest passent (`uv sync && uv run pytest`) | 25% |
| Agrégation cantonale et estimation de population correctes | 20% |
| Qualité des visualisations et de l'analyse | 15% |
| Qualité du code (lisibilité, modularité, documentation) | 5% |
| Bonus : optimisations, visualisations interactives, analyses supplémentaires | 5% |

---

## Stack autorisée

- **Python 3.11+**
- **geopandas** (lecture GeoPackage, spatial join, opérations spatiales)
- **pandas** ou **polars**
- **numpy**, **scipy** (calculs numériques, structures spatiales)
- **scikit-learn** (structures spatiales)
- **matplotlib**, **plotly**, **folium**, **contextily** (visualisation)
- **pyarrow** (export Parquet)
- **pytest**

Toute librairie supplémentaire est autorisée à condition de la justifier.

---

## Consignes

1. Cloner le repo et exécuter `uv sync` pour installer les dépendances.
2. Les données sources sont dans `data/`. Ne pas les modifier.
3. Implémenter le pipeline dans `src/` (3 scripts).
4. Rédiger l'analyse dans `ANALYSIS.md`.
5. Valider avec `uv run pytest` — tous les tests doivent passer.
6. Pousser votre travail sur une branche et ouvrir une Pull Request.

**Bon courage !**
