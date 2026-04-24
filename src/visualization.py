import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import geopandas as gpd

# Chemins
VIZ_DIR = Path(__file__).parent.parent / "output" / "viz"
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "output"
CANTONS_SRC = DATA_DIR / "Togo_Cantons.gpkg"

def create_canton_choropleth(
    cantons_geo: gpd.GeoDataFrame,
    cantons_data: pd.DataFrame,
    category: str,
    output_path: Path,
) -> None:
    """Carte choroplèthe des cantons colorés par distance moyenne avec labels."""
    merged = cantons_geo.merge(cantons_data, on="canton_nom")
    
    col = f"dist_moy_{category}"
    label_map = {"primaire": "Primaire", "college": "Collège", "lycee": "Lycée"}
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    merged.plot(
        column=col,
        cmap="YlOrRd",
        legend=True,
        legend_kwds={"label": f"Distance moyenne (mètres)", "orientation": "vertical"},
        ax=ax,
        edgecolor="black",
        linewidth=0.5
    )
    
    # Ajout des noms des cantons
    for idx, row in merged.iterrows():
        # On utilise le représentant (centroid) du polygone pour placer le texte
        plt.text(
            row.geometry.centroid.x, 
            row.geometry.centroid.y, 
            row.canton_nom, 
            fontsize=8, 
            ha='center',
            fontweight='bold'
        )
    
    ax.set_title(f"Accessibilité scolaire : école {label_map[category]} la plus proche\n(Préfecture de Zio, par canton)", fontsize=14)
    ax.set_axis_off()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def create_comparative_visualization(cantons_data: pd.DataFrame, output_path: Path) -> None:
    """Graphique en barres comparant les distances par catégorie."""
    df_plot = cantons_data.copy().sort_values("dist_moy_primaire")
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = range(len(df_plot))
    width = 0.25
    
    ax.bar([i - width for i in x], df_plot["dist_moy_primaire"], width, label="Primaire", color="#4CAF50")
    ax.bar(x, df_plot["dist_moy_college"], width, label="Collège", color="#2196F3")
    ax.bar([i + width for i in x], df_plot["dist_moy_lycee"], width, label="Lycée", color="#FF9800")
    
    ax.set_ylabel("Distance moyenne pondérée (m)")
    ax.set_title("Comparaison des distances d'accès moyennes par canton et catégorie", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(df_plot["canton_nom"], rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def run() -> None:
    """Produit toutes les visualisations."""
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    
    # Charger les données
    cantons_data = pd.read_parquet(OUTPUT_DIR / "agregation_cantons.parquet")
    cantons_geo = gpd.read_file(CANTONS_SRC)
    cantons_geo = cantons_geo[cantons_geo["prefecture_nom"] == "Zio"]
    
    print("Génération de la carte choroplèthe (Primaire) avec labels...")
    create_canton_choropleth(
        cantons_geo, 
        cantons_data, 
        "primaire", 
        VIZ_DIR / "carte_dist_primaire.png"
    )
    
    print("Génération du graphique comparatif...")
    create_comparative_visualization(
        cantons_data, 
        VIZ_DIR / "comparaison_categories.png"
    )
    
    print("Génération de la carte des zones mal desservies (Lycée) avec labels...")
    merged = cantons_geo.merge(cantons_data, on="canton_nom")
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    merged.plot(ax=ax, color="#f2f2f2", edgecolor="#cccccc")
    
    # Cantons avec dist > 5000m
    critical_zones = merged[merged["dist_moy_lycee"] > 5000]
    critical_zones.plot(
        ax=ax, 
        color="#e74c3c", 
        edgecolor="black"
    )
    
    # Ajout des noms pour TOUS les cantons (ou seulement les critiques pour plus de clarté ?)
    # On ajoute pour tous mais en mettant en gras les critiques
    for idx, row in merged.iterrows():
        is_critical = row.canton_nom in critical_zones.canton_nom.values
        plt.text(
            row.geometry.centroid.x, 
            row.geometry.centroid.y, 
            row.canton_nom, 
            fontsize=8, 
            ha='center',
            color='black' if not is_critical else 'white',
            fontweight='bold' if is_critical else 'normal'
        )
    
    ax.set_title("Zones à desserte critique pour les Lycées\n(Distance moyenne > 5 km)", fontsize=14, color="#c0392b")
    ax.set_axis_off()
    
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color="#e74c3c", lw=4)]
    ax.legend(custom_lines, ["Canton avec distance moyenne > 5km"], loc="lower right")
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "zones_critiques_lycee.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    run()
    print(f"Visualisations enregistrées dans {VIZ_DIR}")
