import re
from pathlib import Path
from typing import Literal

from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


def _get_project_data_path(shortcode: str, mode: Literal["original", "modified"]) -> Path:
    return Path(f"project_data/{shortcode}/OAPs_{mode}")


def serialize_oaps(
    oaps: list[Oap],
    shortcode: str,
    mode: Literal["original", "modified"],
) -> None:
    """Serialize the OAPs to JSON files."""
    if not oaps:
        logger.warning("No OAPs to serialize.")
        return
    folder = _get_project_data_path(shortcode, mode)
    folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing {len(oaps)} OAPs into {folder}")
    for res_oap in oaps:
        filename = re.sub(r"http://rdfh\.ch/[^/]+/", "resource_", res_oap.object_iri)
        with open(folder / f"{filename}.json", mode="w", encoding="utf-8") as f:
            f.write(res_oap.model_dump_json(indent=2))
    logger.info(f"Successfully wrote {len(oaps)} OAPs into {folder}")


def deserialize_oaps(
    shortcode: str,
    mode: Literal["original", "modified"],
) -> list[Oap]:
    """Deserialize the resource OAPs from JSON files."""
    folder = _get_project_data_path(shortcode, mode)
    oaps = []
    for file in [f for f in folder.iterdir() if f.suffix == ".json"]:
        with open(file, mode="r", encoding="utf-8") as f:
            oaps.append(Oap.model_validate_json(f.read()))
    return oaps
