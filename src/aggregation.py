"""
SIG-01 — Agrégation par canton et estimation de la population scolaire

1. Spatial join des points de population avec les polygones cantonaux
2. Estimation de la population scolaire par tranche d'âge (hypothèse homogène)
3. Calcul de la distance moyenne pondérée par canton et par commune

Proportions appliquées :
  - Primaire (6-11 ans) : 14% de la population
  - Collège (12-15 ans) : 12% de la population
  - Lycée (16-18 ans)   : 10% de la population

⚠️ Ces proportions sont une estimation grossière. Elles ne reflètent pas
la réalité démographique locale et pourraient en être significativement
éloignées. De même, la distance moyenne dépend de la résolution spatiale
de la source de population (~30m).
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np

# Chemins
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "output"
CANTONS_PATH = DATA_DIR / "Togo_Cantons.gpkg"

# Proportions de pyramide des âges (hypothèse homogène)
AGE_PROPORTIONS = {
    "primaire": 0.14,    # 6-11 ans
    "college": 0.12,     # 12-15 ans
    "lycee": 0.10,       # 16-18 ans
}


def load_cantons_zio() -> gpd.GeoDataFrame:
    """Charge les polygones cantonaux et filtre sur la préfecture de Zio.

    Returns:
        GeoDataFrame des 16 cantons de Zio
    """
    raise NotImplementedError("À implémenter")


def spatial_join_population_cantons(
    population: pd.DataFrame,
    cantons: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Rattache chaque point de population à son canton via spatial join.

    Ajoute les colonnes canton_nom et commune_nom au DataFrame population.
    """
    raise NotImplementedError("À implémenter")


def estimate_school_population(population: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les colonnes pop_primaire, pop_college, pop_lycee
    en appliquant les proportions à tgo_general_2020."""
    raise NotImplementedError("À implémenter")


def aggregate_by_canton(
    population: pd.DataFrame,
    etablissements: gpd.GeoDataFrame,
    cantons: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Agrège les indicateurs par canton.

    Pour chaque canton :
    - population_totale : somme des tgo_general_2020
    - pop_primaire, pop_college, pop_lycee : population scolaire estimée
    - dist_moy_primaire, dist_moy_college, dist_moy_lycee :
      distance moyenne pondérée par la population scolaire
    - nb_primaire, nb_college, nb_lycee :
      nombre d'établissements de chaque catégorie dans le canton

    Formule de la moyenne pondérée :
        Σ(distance_i × pop_scolaire_i) / Σ(pop_scolaire_i)
    """
    raise NotImplementedError("À implémenter")


def aggregate_by_commune(canton_data: pd.DataFrame) -> pd.DataFrame:
    """Agrège les résultats cantonaux au niveau communal.

    Retourne un DataFrame avec 4 lignes communes + 1 ligne "Total".
    """
    raise NotImplementedError("À implémenter")


def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Point d'entrée : charge, joint, agrège, exporte."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Charger distances pré-calculées
    distances_path = OUTPUT_DIR / "population_distances.parquet"
    if not distances_path.exists():
        raise FileNotFoundError(
            f"{distances_path} introuvable. Exécutez d'abord distance_calculation.py"
        )

    population = pd.read_parquet(distances_path)
    cantons = load_cantons_zio()
    etablissements = gpd.read_file(DATA_DIR / "Etablissement_scolaire_Zio.gpkg")

    population = spatial_join_population_cantons(population, cantons)
    population = estimate_school_population(population)

    cantons_result = aggregate_by_canton(population, etablissements, cantons)
    communes_result = aggregate_by_commune(cantons_result)

    cantons_result.to_parquet(OUTPUT_DIR / "agregation_cantons.parquet", index=False)
    communes_result.to_parquet(OUTPUT_DIR / "agregation_communes.parquet", index=False)

    print(f"Agrégation cantons : {len(cantons_result)} lignes")
    print(f"Agrégation communes : {len(communes_result)} lignes")

    return cantons_result, communes_result


if __name__ == "__main__":
    cantons_df, communes_df = run()
    print(f"\n=== Par canton ===\n{cantons_df.to_string(index=False)}")
    print(f"\n=== Par commune ===\n{communes_df.to_string(index=False)}")
