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
    """Charge les polygones cantonaux et filtre sur la préfecture de Zio."""
    cantons = gpd.read_file(CANTONS_PATH)
    # Filtrage sur la préfecture cible
    cantons_zio = cantons[cantons["prefecture_nom"] == "Zio"].copy()
    return cantons_zio


def spatial_join_population_cantons(
    population: pd.DataFrame,
    cantons: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Rattache chaque point de population à son canton via spatial join.
    
    On convertit le DataFrame population en GeoDataFrame pour l'opération.
    """
    # Récupération des points originaux pour la géométrie
    pop_geo = gpd.read_file(DATA_DIR / "Population_Zio.gpkg")
    population_gdf = gpd.GeoDataFrame(
        population, 
        geometry=pop_geo.geometry, 
        crs=pop_geo.crs
    )
    
    # Jointure spatiale : on veut savoir dans quel polygone (canton) se trouve chaque point
    # On ne garde que les colonnes utiles du canton pour éviter les doublons de noms
    cantons_subset = cantons[["canton_nom", "commune_nom", "geometry"]]
    joined = gpd.sjoin(population_gdf, cantons_subset, how="left", predicate="intersects")
    
    return pd.DataFrame(joined.drop(columns=["geometry", "index_right"]))


def estimate_school_population(population: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les colonnes pop_primaire, pop_college, pop_lycee."""
    df = population.copy()
    for cat, prop in AGE_PROPORTIONS.items():
        df[f"pop_{cat}"] = df["tgo_general_2020"] * prop
    return df


def aggregate_by_canton(
    population: pd.DataFrame,
    etablissements: gpd.GeoDataFrame,
    cantons: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Agrège les indicateurs par canton avec calcul de moyenne pondérée."""
    
    # 1. Calcul des statistiques par canton sur la population
    # On définit les agrégations pour les sommes
    agg_funcs = {
        "tgo_general_2020": "sum",
        "pop_primaire": "sum",
        "pop_college": "sum",
        "pop_lycee": "sum",
    }
    
    # Pour les distances moyennes pondérées, on le fait manuellement après le groupby
    def weighted_avg(group, dist_col, weight_col):
        if group[weight_col].sum() == 0:
            return 0
        return np.average(group[dist_col], weights=group[weight_col])

    canton_groups = population.groupby(["canton_nom", "commune_nom"])
    
    # Sommes de populations
    res = canton_groups.agg(agg_funcs).reset_index()
    res = res.rename(columns={"tgo_general_2020": "population_totale"})
    
    # Distances moyennes pondérées
    for cat in ["primaire", "college", "lycee"]:
        res[f"dist_moy_{cat}"] = res.apply(
            lambda x: weighted_avg(
                population[population["canton_nom"] == x["canton_nom"]], 
                f"dist_{cat}", 
                f"pop_{cat}"
            ), 
            axis=1
        )

    # 2. Comptage des établissements par canton
    # Il faut d'abord rattacher les établissements aux cantons spatialement
    etab_with_canton = gpd.sjoin(etablissements, cantons[["canton_nom", "geometry"]], how="left", predicate="intersects")
    
    # Mapping catégories -> colonnes
    cat_map = {
        "Ecole primaire": "nb_primaire",
        "College": "nb_college",
        "Lycée": "nb_lycee",
    }
    
    for etab_cat, col_name in cat_map.items():
        counts = etab_with_canton[etab_with_canton["etablissement_categorie"] == etab_cat].groupby("canton_nom").size()
        res[col_name] = res["canton_nom"].map(counts).fillna(0).astype(int)

    return res


def aggregate_by_commune(canton_data: pd.DataFrame) -> pd.DataFrame:
    """Agrège les résultats cantonaux au niveau communal."""
    
    # Liste des colonnes à sommer
    sum_cols = [
        "population_totale", "pop_primaire", "pop_college", "pop_lycee",
        "nb_primaire", "nb_college", "nb_lycee"
    ]
    
    # Pour les distances moyennes au niveau commune, on re-pondère par les populations scolaires cantonales
    def commune_weighted_avg(group, dist_prefix):
        pop_col = f"pop_{dist_prefix}"
        dist_col = f"dist_moy_{dist_prefix}"
        if group[pop_col].sum() == 0:
            return 0
        return np.average(group[dist_col], weights=group[pop_col])

    commune_res = []
    for commune, group in canton_data.groupby("commune_nom"):
        row = {"commune_nom": commune}
        for col in sum_cols:
            row[col] = group[col].sum()
        for cat in ["primaire", "college", "lycee"]:
            row[f"dist_moy_{cat}"] = commune_weighted_avg(group, cat)
        commune_res.append(row)
        
    df_communes = pd.DataFrame(commune_res)
    
    # Ligne Total
    total_row = {"commune_nom": "Total"}
    for col in sum_cols:
        total_row[col] = df_communes[col].sum()
    for cat in ["primaire", "college", "lycee"]:
        total_row[f"dist_moy_{cat}"] = np.average(df_communes[f"dist_moy_{cat}"], weights=df_communes[f"pop_{cat}"])
        
    return pd.concat([df_communes, pd.DataFrame([total_row])], ignore_index=True)


def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Point d'entrée : charge, joint, agrège, exporte."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    distances_path = OUTPUT_DIR / "population_distances.parquet"
    if not distances_path.exists():
        raise FileNotFoundError(f"{distances_path} introuvable. Exécutez d'abord distance_calculation.py")

    print("Chargement des données...")
    population = pd.read_parquet(distances_path)
    cantons = load_cantons_zio()
    etablissements = gpd.read_file(DATA_DIR / "Etablissement_scolaire_Zio.gpkg")

    print("Jointure spatiale (Population <-> Cantons)...")
    population = spatial_join_population_cantons(population, cantons)
    
    print("Estimation de la population scolaire...")
    population = estimate_school_population(population)

    print("Agrégation par canton...")
    cantons_result = aggregate_by_canton(population, etablissements, cantons)
    
    print("Agrégation par commune...")
    communes_result = aggregate_by_commune(cantons_result)

    cantons_result.to_parquet(OUTPUT_DIR / "agregation_cantons.parquet", index=False)
    communes_result.to_parquet(OUTPUT_DIR / "agregation_communes.parquet", index=False)

    return cantons_result, communes_result


if __name__ == "__main__":
    cantons_df, communes_df = run()
    print(f"\nAgrégation terminée : {len(cantons_df)} cantons et {len(communes_df)-1} communes traités.")
    cols_show = ["commune_nom", "population_totale", "dist_moy_primaire", "nb_primaire"]
    print(f"\nAperçu par commune :\n{communes_df[cols_show].to_string(index=False)}")
