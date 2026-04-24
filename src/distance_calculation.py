from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

# Chemins
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "output"
ETAB_PATH = DATA_DIR / "Etablissement_scolaire_Zio.gpkg"
POP_PATH = DATA_DIR / "Population_Zio.gpkg"

# Projection locale pour le Togo (mètres)
LOCAL_CRS = "EPSG:32631"  # UTM Zone 31N

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
    etablissements = gpd.read_file(ETAB_PATH)
    population = gpd.read_file(POP_PATH)
    return etablissements, population


def compute_nearest_distance(
    pop_coords: np.ndarray,
    etab_coords: np.ndarray,
) -> np.ndarray:
    """Calcule la distance en mètres de chaque point population
    à l'établissement le plus proche en utilisant un cKDTree.

    Args:
        pop_coords: array (N, 2) de coordonnées en mètres (UTM)
        etab_coords: array (M, 2) de coordonnées en mètres (UTM)

    Returns:
        array (N,) de distances en mètres
    """
    tree = cKDTree(etab_coords)
    distances, _ = tree.query(pop_coords, k=1)
    return distances


def compute_all_distances(
    population: gpd.GeoDataFrame,
    etablissements: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Calcule les distances pour les 3 catégories d'établissement.

    Retourne le DataFrame population enrichi de 3 colonnes :
    dist_primaire, dist_college, dist_lycee (en mètres).
    """
    # Reprojection en UTM 31N pour avoir des mètres
    pop_projected = population.to_crs(LOCAL_CRS)
    etab_projected = etablissements.to_crs(LOCAL_CRS)

    # Coordonnées des points de population (N, 2)
    # Les points de population peuvent être des MultiPoints d'après le README
    # On récupère le centroïde pour être sûr d'avoir un point x,y
    pop_coords = np.array(list(zip(pop_projected.geometry.centroid.x, pop_projected.geometry.centroid.y)))

    # Pour chaque catégorie, calcul de la distance la plus proche
    result_df = population.drop(columns='geometry').copy()

    for cat_name, col_name in CATEGORIES.items():
        # Filtrer les établissements par catégorie
        etab_cat = etab_projected[etab_projected["etablissement_categorie"] == cat_name]
        
        if etab_cat.empty:
            print(f"Attention: Aucun établissement trouvé pour la catégorie {cat_name}")
            result_df[col_name] = np.nan
            continue

        # Les établissements sont des Points
        etab_coords = np.array(list(zip(etab_cat.geometry.x, etab_cat.geometry.y)))
        
        # Calcul des distances
        distances = compute_nearest_distance(pop_coords, etab_coords)
        result_df[col_name] = distances

    return result_df


def run() -> pd.DataFrame:
    """Point d'entrée : charge, calcule, exporte, retourne le résultat."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Chargement des données...")
    etablissements, population = load_data()
    
    print("Calcul des distances (cKDTree + UTM 31N)...")
    result = compute_all_distances(population, etablissements)

    output_path = OUTPUT_DIR / "population_distances.parquet"
    result.to_parquet(output_path, index=False)
    print(f"Distances exportées : {output_path}")

    return result


if __name__ == "__main__":
    import time
    start_time = time.time()
    result = run()
    duration = time.time() - start_time
    print(f"\nDistances calculées en {duration:.1f}s pour {len(result)} points de population")
    for col in CATEGORIES.values():
        print(f"  {col}: médiane = {result[col].median():.0f}m")
