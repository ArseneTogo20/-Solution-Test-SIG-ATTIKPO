import pytest
from pathlib import Path
import pandas as pd

# Chemins
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
VIZ_DIR = ROOT_DIR / "output" / "viz"

# Constantes de référence
TOTAL_POPULATION_POINTS = 112_466
TOTAL_POPULATION_ESTIMATE = 293_014  # ±5%
NB_ECOLES_PRIMAIRES = 533
NB_COLLEGES = 173
NB_LYCEES = 57
NB_CANTONS_ZIO = 16
COMMUNES = ["Zio 1", "Zio 2", "Zio 3", "Zio 4"]

PROP_PRIMAIRE = 0.14
PROP_COLLEGE = 0.12
PROP_LYCEE = 0.10


@pytest.fixture
def output_dir():
    return OUTPUT_DIR

@pytest.fixture
def viz_dir():
    return VIZ_DIR

def load_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)
