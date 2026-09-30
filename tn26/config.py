"""Global configuration, directory paths, electoral constants, and alliance definitions."""
from pathlib import Path
from typing import Dict, List, Set

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = ROOT_DIR / "data"
DATA_RAW_DIR: Path = DATA_DIR / "raw"
DATA_PROCESSED_DIR: Path = DATA_DIR / "processed"
DATA_GEO_DIR: Path = DATA_DIR / "geo"
DOCS_DIR: Path = ROOT_DIR / "docs"
PLOTS_DIR: Path = ROOT_DIR / "plots"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Total assembly constituencies in Tamil Nadu Legislative Assembly
TOTAL_ASSEMBLY_SEATS: int = 234
MAJORITY_SEAT_THRESHOLD: int = 118

# Major political alliances in 2026 Tamil Nadu election
# Secular Progressive Alliance (SPA) led by Dravida Munnetra Kazhagam (DMK)
SPA_PARTIES: Set[str] = {
    "DMK",
    "INC",
    "VCK",
    "CPI",
    "CPI(M)",
    "IUML",
    "DMDK",
    "MDMK",
    "KMDK"
}

# National Democratic Alliance (NDA) / AIADMK Front
AIADMK_FRONT_PARTIES: Set[str] = {
    "ADMK",
    "BJP",
    "PMK",
    "AMMKMNKZ",
    "PT",
    "TMC(M)"
}

# Insurgent / Standalone entities
TVK_PARTY: str = "TVK"
NTK_PARTY: str = "NTK"

# Geopolitical regions mapping AC ranges
REGIONAL_CLUSTERS: Dict[str, List[int]] = {
    "Chennai Metropolitan": list(range(1, 29)),
    "Northern Tamil Nadu": list(range(29, 90)),
    "Western Tamil Nadu (Kongu)": list(range(90, 131)),
    "Cauvery Delta": list(range(131, 179)),
    "Southern Tamil Nadu": list(range(179, 225)),
    "Deep South": list(range(225, 235)),
}

# Official color palette for publication-grade visualization
PARTY_COLOR_MAP: Dict[str, str] = {
    "TVK": "#C41E3A",          # Cardinal Red / TVK Saffron-Yellow-Red
    "DMK": "#E31B23",          # DMK Red & Black representation
    "ADMK": "#00873E",         # AIADMK Green
    "BJP": "#FF9933",          # BJP Saffron
    "INC": "#19AAED",          # Congress Blue
    "VCK": "#000080",          # VCK Navy Blue
    "PMK": "#FFDF00",          # PMK Yellow
    "NTK": "#8B0000",          # NTK Maroon / Deep Crimson
    "Independent / Other": "#808080",
}

BLOC_COLOR_MAP: Dict[str, str] = {
    "TVK": "#C41E3A",
    "DMK-led bloc": "#003366",
    "AIADMK-led bloc": "#00873E",
    "NTK": "#8B0000",
    "Other": "#808080",
}

# Ground truth outcome validation constants
GROUND_TRUTH_2026: Dict[str, int] = {
    "TVK": 108,
    "DMK_led_bloc": 73,
    "AIADMK_led_bloc": 53,
    "NTK": 0,
    "Other": 0,
}

RANDOM_SEED: int = 42
