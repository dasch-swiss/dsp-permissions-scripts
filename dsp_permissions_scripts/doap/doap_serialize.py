import json
from pathlib import Path
from typing import Literal

from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import DoapTargetType
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import get_timestamp

logger = get_logger(__name__)


def _get_file_path(shortcode: str, mode: Literal["original", "modified"]) -> Path:
    return Path(f"project_data/{shortcode}/DOAPs_{mode}.json")


def serialize_doaps_of_project(
    project_doaps: list[Doap],
    shortcode: str,
    mode: Literal["original", "modified"],
    host: str,
    target_type: DoapTargetType = DoapTargetType.ALL,
) -> None:
    """Serialize the DOAPs of a project to a JSON file."""
    filepath = _get_file_path(shortcode, mode)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    explanation_string = f"{get_timestamp()}: Project {shortcode} on host {host} has {len(project_doaps)} DOAPs"
    if target_type != DoapTargetType.ALL:
        explanation_string += f" which are related to a {target_type}"
    doaps_as_dicts = [doap.model_dump(exclude_none=True, mode="json") for doap in project_doaps]
    doaps_as_dict = {explanation_string: doaps_as_dicts}
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(doaps_as_dict, ensure_ascii=False, indent=2))
    logger.info(f"{len(project_doaps)} DOAPs have been written to file {filepath}")


def deserialize_doaps_of_project(
    shortcode: str,
    mode: Literal["original", "modified"],
) -> list[Doap]:
    """Deserialize the DOAPs of a project from a JSON file."""
    filepath = _get_file_path(shortcode, mode)
    with open(filepath, mode="r", encoding="utf-8") as f:
        doaps_as_dict = json.load(f)
    doaps_as_dicts = next(iter(doaps_as_dict.values()))
    return [Doap.model_validate(d) for d in doaps_as_dicts]
