import json
from pathlib import Path
from typing import Literal

from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp

logger = get_logger(__name__)


def _get_file_path(shortcode: str, mode: Literal["original", "modified"]) -> Path:
    return Path(f"project_data/{shortcode}/APs_{mode}.json")


def serialize_aps_of_project(
    project_aps: list[Ap],
    shortcode: str,
    mode: Literal["original", "modified"],
    host: str,
) -> None:
    """Serialize the APs of a project to a JSON file."""
    filepath = _get_file_path(shortcode, mode)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    explanation_string = f"{get_timestamp()}: Project {shortcode} on host {host} has {len(project_aps)} APs"
    aps_as_dicts = [ap.model_dump(exclude_none=True, mode="json") for ap in project_aps]
    aps_as_dict = {explanation_string: aps_as_dicts}
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(aps_as_dict, ensure_ascii=False, indent=2))
    print(f"{len(project_aps)} APs have been written to file {str(filepath)}")
    logger.info(f"{len(project_aps)} APs have been written to file {str(filepath)}")


def deserialize_aps_of_project(
    shortcode: str,
    mode: Literal["original", "modified"],
) -> list[Ap]:
    """Deserialize the APs of a project from a JSON file."""
    filepath = _get_file_path(shortcode, mode)
    with open(filepath, mode="r", encoding="utf-8") as f:
        aps_as_dict = json.load(f)
    aps_as_dicts = list(aps_as_dict.values())[0]
    return [Ap.model_validate(d) for d in aps_as_dicts]
