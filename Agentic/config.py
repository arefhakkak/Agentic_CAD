# config/config.py
import logging
import os
from pathlib import Path

import yaml

# ── Configuration loading ────────────────────────────────


def load_config(path="config.yaml"):
    # Get the directory where this config.py file is located
    config_dir = Path(__file__).parent
    config_path = config_dir / path
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()


# ── Centralized logger ─────────────────────────────

LOG_DIR = Path(CONFIG.get("log_dir", "project_saab/logs"))
LOG_FILE = CONFIG.get("log_file", "project.log")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = CONFIG.get("log_level", "INFO").upper()

logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,  # Uncomment for debug level
    # format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    format="%(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("project_hallins")
