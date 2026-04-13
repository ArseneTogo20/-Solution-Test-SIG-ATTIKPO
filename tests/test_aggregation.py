import pytest
import pandas as pd
from pathlib import Path
from tests.conftest import (
    OUTPUT_DIR,
    TOTAL_POPULATION_ESTIMATE,
    NB_ECOLES_PRIMAIRES,
    NB_COLLEGES,
    NB_LYCEES,
    NB_CANTONS_ZIO,
    COMMUNES,
    PROP_PRIMAIRE,
    PROP_COLLEGE,
    PROP_LYCEE,
)

CANTONS_PATH = OUTPUT_DIR / "agregation_cantons.parquet"
COMMUNES_PATH = OUTPUT_DIR / "agregation_communes.parquet"

REQUIRED_CANTON_COLUMNS = [
    "canton_nom", "commune_nom", "population_totale",
    "pop_primaire", "pop_college", "pop_lycee",
    "dist_moy_primaire", "dist_moy_college", "dist_moy_lycee",
    "nb_primaire", "nb_college", "nb_lycee",
]


@pytest.fixture(scope="module")
def cantons_df():
    return pd.read_parquet(CANTONS_PATH)


@pytest.fixture(scope="module")
def communes_df():
    return pd.read_parquet(COMMUNES_PATH)


# --- Tests cantons ---

def test_cantons_file_exists():
    assert CANTONS_PATH.exists(), (
        "Le fichier data/output/agregation_cantons.parquet n'existe pas. "
        "Exécutez d'abord src/aggregation.py"
    )


def test_cantons_row_count(cantons_df):
    assert len(cantons_df) == NB_CANTONS_ZIO, (
        f"Nombre de cantons attendu : {NB_CANTONS_ZIO}, obtenu : {len(cantons_df)}"
    )


def test_cantons_required_columns(cantons_df):
    for col in REQUIRED_CANTON_COLUMNS:
        assert col in cantons_df.columns, f"Colonne manquante : {col}"


def test_cantons_population_total(cantons_df):
    total = cantons_df["population_totale"].sum()
    low = TOTAL_POPULATION_ESTIMATE * 0.95
    high = TOTAL_POPULATION_ESTIMATE * 1.05
    assert low <= total <= high, (
        f"Population totale = {total:.0f} hors de la plage attendue "
        f"[{low:.0f}, {high:.0f}] (~{TOTAL_POPULATION_ESTIMATE})"
    )


def test_cantons_pop_primaire_proportion(cantons_df):
    for _, row in cantons_df.iterrows():
        ratio = row["pop_primaire"] / row["population_totale"]
        assert abs(ratio - PROP_PRIMAIRE) < 0.01, (
            f"Canton {row['canton_nom']} : ratio pop_primaire/population_totale = "
            f"{ratio:.3f}, attendu {PROP_PRIMAIRE} ± 0.01"
        )


def test_cantons_pop_college_proportion(cantons_df):
    for _, row in cantons_df.iterrows():
        ratio = row["pop_college"] / row["population_totale"]
        assert abs(ratio - PROP_COLLEGE) < 0.01, (
            f"Canton {row['canton_nom']} : ratio pop_college/population_totale = "
            f"{ratio:.3f}, attendu {PROP_COLLEGE} ± 0.01"
        )


def test_cantons_pop_lycee_proportion(cantons_df):
    for _, row in cantons_df.iterrows():
        ratio = row["pop_lycee"] / row["population_totale"]
        assert abs(ratio - PROP_LYCEE) < 0.01, (
            f"Canton {row['canton_nom']} : ratio pop_lycee/population_totale = "
            f"{ratio:.3f}, attendu {PROP_LYCEE} ± 0.01"
        )


def test_cantons_distances_positive(cantons_df):
    for col in ["dist_moy_primaire", "dist_moy_college", "dist_moy_lycee"]:
        assert (cantons_df[col] > 0).all(), (
            f"Des distances nulles ou négatives détectées dans {col}"
        )


def test_cantons_distances_realistic(cantons_df):
    for val in cantons_df["dist_moy_primaire"]:
        assert 200 <= val <= 15_000, (
            f"dist_moy_primaire = {val:.0f}m hors plage réaliste [200m, 15000m]"
        )


def test_cantons_nb_primaire_total(cantons_df):
    total = cantons_df["nb_primaire"].sum()
    assert total == NB_ECOLES_PRIMAIRES, (
        f"Somme nb_primaire = {total}, attendu {NB_ECOLES_PRIMAIRES}"
    )


def test_cantons_nb_college_total(cantons_df):
    total = cantons_df["nb_college"].sum()
    assert total == NB_COLLEGES, (
        f"Somme nb_college = {total}, attendu {NB_COLLEGES}"
    )


def test_cantons_nb_lycee_total(cantons_df):
    total = cantons_df["nb_lycee"].sum()
    assert total == NB_LYCEES, (
        f"Somme nb_lycee = {total}, attendu {NB_LYCEES}"
    )


def test_cantons_no_null(cantons_df):
    metric_cols = [c for c in REQUIRED_CANTON_COLUMNS if c not in ("canton_nom", "commune_nom")]
    for col in metric_cols:
        null_count = cantons_df[col].isna().sum()
        assert null_count == 0, f"{null_count} valeurs nulles dans {col}"


# --- Tests communes ---

def test_communes_file_exists():
    assert COMMUNES_PATH.exists(), (
        "Le fichier data/output/agregation_communes.parquet n'existe pas. "
        "Exécutez d'abord src/aggregation.py"
    )


def test_communes_row_count(communes_df):
    assert len(communes_df) >= 5, (
        f"Nombre de lignes attendu : ≥ 5 (4 communes + 1 total), obtenu : {len(communes_df)}"
    )


def test_communes_all_present(communes_df):
    commune_col = "commune_nom" if "commune_nom" in communes_df.columns else "commune"
    present = communes_df[commune_col].tolist()
    for commune in COMMUNES:
        assert commune in present, (
            f"Commune '{commune}' absente du fichier agrégation_communes.parquet"
        )


def test_communes_distances_positive(communes_df):
    dist_cols = [c for c in communes_df.columns if c.startswith("dist_")]
    for col in dist_cols:
        non_null = communes_df[col].dropna()
        assert (non_null > 0).all(), f"Distances négatives ou nulles dans {col}"


def test_communes_no_null(communes_df):
    numeric_cols = communes_df.select_dtypes("number").columns
    for col in numeric_cols:
        commune_col = "commune_nom" if "commune_nom" in communes_df.columns else "commune"
        non_total = communes_df[communes_df[commune_col] != "Total"]
        null_count = non_total[col].isna().sum()
        assert null_count == 0, f"{null_count} valeurs nulles dans {col} (hors ligne Total)"
