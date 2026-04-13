"""
SIG-01 — Calcul de la distance à l'école la plus proche

Pour chaque point de population (~112 000 points), calculer la distance
en mètres à l'établissement scolaire le plus proche, par catégorie
(primaire, collège, lycée).

Performance attendue : le calcul complet doit s'exécuter en moins de 2 minutes.
Avec 112 466 × 533 paires pour la catégorie primaire seule, une approche naïve
sera trop lente — réfléchissez à une méthode efficace.
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np

# Chemins
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "output"
ETAB_PATH = DATA_DIR / "Etablissement_scolaire_Zio.gpkg"
POP_PATH = DATA_DIR / "Population_Zio.gpkg"

# Catégories d'établissements à traiter
CATEGORIES = {
    "Ecole primaire": "dist_primaire",
    "College": "dist_college",
    "Lycée": "dist_lycee",
}


def load_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Charge les deux GeoPackages.

    Returns:
        (etablissements, population)
    """
    raise NotImplementedError("À implémenter")


def compute_nearest_distance(
    pop_coords: np.ndarray,
    etab_coords: np.ndarray,
) -> np.ndarray:
    """Calcule la distance en mètres de chaque point population
    à l'établissement le plus proche.

    Args:
        pop_coords: array (N, 2) de coordonnées
        etab_coords: array (M, 2) de coordonnées

    Returns:
        array (N,) de distances en mètres

    Note: le candidat choisit et justifie son approche :
    - Quelle métrique de distance ? (haversine, projection locale, ...)
    - Quelle structure de données pour accélérer la recherche ?
    """
    raise NotImplementedError("À implémenter")


def compute_all_distances(
    population: gpd.GeoDataFrame,
    etablissements: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Calcule les distances pour les 3 catégories d'établissement.

    Retourne le DataFrame population enrichi de 3 colonnes :
    dist_primaire, dist_college, dist_lycee (en mètres).
    """
    raise NotImplementedError("À implémenter")


def run() -> pd.DataFrame:
    """Point d'entrée : charge, calcule, exporte, retourne le résultat."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    etablissements, population = load_data()
    result = compute_all_distances(population, etablissements)

    output_path = OUTPUT_DIR / "population_distances.parquet"
    result.to_parquet(output_path, index=False)
    print(f"Distances exportées : {output_path}")

    return result


if __name__ == "__main__":
    result = run()
    print(f"\nDistances calculées pour {len(result)} points de population")
    for col in CATEGORIES.values():
        print(f"  {col}: médiane = {result[col].median():.0f}m")
