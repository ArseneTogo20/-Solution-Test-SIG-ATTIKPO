import pytest
import time
from pathlib import Path
from tests.conftest import (
    OUTPUT_DIR,
    TOTAL_POPULATION_POINTS,
)


@pytest.fixture(scope="module")
def distance_result():
    from src.distance_calculation import run
    start = time.time()
    result = run()
    elapsed = time.time() - start
    return result, elapsed


def test_output_file_exists():
    assert (OUTPUT_DIR / "population_distances.parquet").exists(), (
        "Le fichier data/output/population_distances.parquet n'existe pas. "
        "Exécutez d'abord src/distance_calculation.py"
    )


def test_result_has_distance_columns(distance_result):
    result, _ = distance_result
    for col in ["dist_primaire", "dist_college", "dist_lycee"]:
        assert col in result.columns, f"Colonne manquante : {col}"


def test_result_row_count(distance_result):
    result, _ = distance_result
    assert len(result) == TOTAL_POPULATION_POINTS, (
        f"Nombre de lignes attendu : {TOTAL_POPULATION_POINTS}, obtenu : {len(result)}"
    )


def test_distances_positive(distance_result):
    result, _ = distance_result
    for col in ["dist_primaire", "dist_college", "dist_lycee"]:
        assert (result[col] > 0.1).all(), (
            f"Des distances négatives ou nulles détectées dans {col}"
        )


def test_distances_in_meters(distance_result):
    result, _ = distance_result
    median_primaire = result["dist_primaire"].median()
    assert 200 <= median_primaire <= 8_000, (
        f"Médiane dist_primaire = {median_primaire:.0f}m — probable erreur de conversion "
        f"(attendu entre 200m et 8000m)"
    )


def test_distances_realistic_per_category(distance_result):
    result, _ = distance_result
    checks = [
        ("dist_primaire", 200, 6_000),
        ("dist_college", 500, 15_000),
        ("dist_lycee", 1_000, 25_000),
    ]
    for col, low, high in checks:
        median = result[col].median()
        assert low <= median <= high, (
            f"Médiane {col} = {median:.0f}m hors de la plage réaliste [{low}m, {high}m]"
        )


def test_primaire_shorter_than_lycee(distance_result):
    result, _ = distance_result
    median_primaire = result["dist_primaire"].median()
    median_lycee = result["dist_lycee"].median()
    assert median_primaire < median_lycee, (
        f"Médiane dist_primaire ({median_primaire:.0f}m) >= médiane dist_lycee "
        f"({median_lycee:.0f}m) — incohérent"
    )


def test_no_null_distances(distance_result):
    result, _ = distance_result
    for col in ["dist_primaire", "dist_college", "dist_lycee"]:
        null_count = result[col].isna().sum()
        assert null_count == 0, f"{null_count} valeurs nulles dans {col}"


def test_performance(distance_result):
    _, elapsed = distance_result
    assert elapsed < 120, (
        f"Calcul trop lent : {elapsed:.1f}s (limite : 120s). "
        "Utilisez une structure spatiale efficace (BallTree, KDTree...)"
    )
