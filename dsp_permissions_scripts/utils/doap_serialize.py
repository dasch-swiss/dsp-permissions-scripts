import json
from pathlib import Path
from typing import Literal

from dsp_permissions_scripts.models.doap import Doap, DoapTargetType


def _get_file_path(
    shortcode: str,
    mode: Literal["original", "modified"]
) -> Path:
    return Path(f"project_data/{shortcode}/DOAPs_{mode}.json")


def serialize_doaps_of_project(
    project_doaps: list[Doap],
    shortcode: str,
    mode: Literal["original", "modified"],
    target: DoapTargetType = DoapTargetType.ALL,
) -> None:
    """Serialize the DOAPs of a project to a JSON file."""
    filepath = _get_file_path(shortcode, mode)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    explanation_string = f"Project {shortcode} has {len(project_doaps)} DOAPs"
    if target != DoapTargetType.ALL:
        explanation_string += f" which are related to a {target}"
    doaps_as_dicts = [doap.model_dump(exclude_none=True) for doap in project_doaps]
    doaps_as_dict = {explanation_string: doaps_as_dicts}
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(doaps_as_dict, ensure_ascii=False, indent=2))


def deserialize_doaps_of_project(
    shortcode: str,
    mode: Literal["original", "modified"],
) -> list[Doap]:
    """Deserialize the DOAPs of a project from a JSON file."""
    filepath = _get_file_path(shortcode, mode)
    with open(filepath, mode="r", encoding="utf-8") as f:
        doaps_as_dict = json.load(f)
    doaps_as_dicts = doaps_as_dict.values()[0]
    return [Doap.model_validate(d) for d in doaps_as_dicts]
