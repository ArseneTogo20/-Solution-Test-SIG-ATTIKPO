"""
SIG-01 — Visualisation de l'accessibilité scolaire

Produire 2-3 cartes/graphiques montrant :
- Carte choroplèthe des cantons par distance moyenne d'accès
- Zones les plus mal desservies
- Comparaison entre catégories ou entre cantons

Les visualisations sont enregistrées dans output/viz/
"""

from pathlib import Path
import pandas as pd
import geopandas as gpd

# Chemins
VIZ_DIR = Path(__file__).parent.parent / "output" / "viz"
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "output"


def create_canton_choropleth(
    cantons_geo: gpd.GeoDataFrame,
    cantons_data: pd.DataFrame,
    category: str,
    output_path: Path,
) -> None:
    """Carte choroplèthe des cantons colorés par distance moyenne.

    Args:
        cantons_geo: GeoDataFrame avec les géométries cantonales
        cantons_data: DataFrame avec les indicateurs par canton
        category: "primaire", "college" ou "lycee"
        output_path: chemin de sortie (PNG ou HTML)
    """
    raise NotImplementedError("À implémenter")


def create_underserved_map(output_path: Path) -> None:
    """Carte mettant en évidence les zones/cantons mal desservis.

    Le candidat définit et justifie le seuil de distance.
    """
    raise NotImplementedError("À implémenter")


def create_comparative_visualization(output_path: Path) -> None:
    """Visualisation comparative entre catégories ou entre cantons."""
    raise NotImplementedError("À implémenter")


def run() -> None:
    """Produit toutes les visualisations."""
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    raise NotImplementedError("À implémenter")


if __name__ == "__main__":
    run()
    print(f"Visualisations enregistrées dans {VIZ_DIR}")
