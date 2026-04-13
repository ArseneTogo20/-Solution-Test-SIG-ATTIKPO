import pytest
from pathlib import Path
from tests.conftest import VIZ_DIR

ROOT_DIR = Path(__file__).parent.parent
ANALYSIS_PATH = ROOT_DIR / "ANALYSIS.md"
VIZ_EXTENSIONS = {".png", ".html", ".jpg", ".svg"}
MIN_FILE_SIZE_KB = 10


def test_viz_directory_has_files():
    viz_files = [
        f for f in VIZ_DIR.iterdir()
        if f.suffix.lower() in VIZ_EXTENSIONS
    ] if VIZ_DIR.exists() else []
    assert len(viz_files) >= 2, (
        f"output/viz/ contient {len(viz_files)} fichier(s) de visualisation, "
        f"minimum attendu : 2 (extensions acceptées : {VIZ_EXTENSIONS})"
    )


def test_viz_files_not_empty():
    if not VIZ_DIR.exists():
        pytest.skip("Dossier output/viz/ absent")
    viz_files = [
        f for f in VIZ_DIR.iterdir()
        if f.suffix.lower() in VIZ_EXTENSIONS
    ]
    for f in viz_files:
        size_kb = f.stat().st_size / 1024
        assert size_kb > MIN_FILE_SIZE_KB, (
            f"{f.name} fait {size_kb:.1f} KB — fichier probablement vide ou corrompu "
            f"(minimum attendu : {MIN_FILE_SIZE_KB} KB)"
        )


def test_analysis_exists():
    assert ANALYSIS_PATH.exists(), "ANALYSIS.md est absent à la racine du repo"


def test_analysis_not_template():
    if not ANALYSIS_PATH.exists():
        pytest.skip("ANALYSIS.md absent")
    content = ANALYSIS_PATH.read_text(encoding="utf-8")
    assert len(content) > 500, (
        f"ANALYSIS.md contient seulement {len(content)} caractères — "
        "veuillez rédiger votre analyse (minimum 500 caractères)"
    )
    assert "Votre analyse ici" not in content, (
        "ANALYSIS.md contient encore le texte du template — "
        "veuillez remplacer les sections par votre analyse"
    )
