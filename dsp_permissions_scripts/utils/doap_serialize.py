import json
from pathlib import Path
from typing import Literal

from dsp_permissions_scripts.models.doap import Doap


def _get_file_path(
    shortcode: str,
    mode: Literal["original", "modified"]
) -> Path:
    return Path(f"project_data/{shortcode}/DOAPs_{mode}.json")


def serialize_project_doaps(
    project_doaps: list[Doap],
    shortcode: str,
    mode: Literal["original", "modified"],
) -> None:
    """Serialize the resource DOAPs to a JSON file."""
    filepath = _get_file_path(shortcode, mode)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    doaps_as_dicts = [doap.model_dump(exclude_none=True) for doap in project_doaps]
    doaps_as_dict = {f"Project {shortcode} has {len(project_doaps)} DOAPs": doaps_as_dicts}
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(doaps_as_dict, ensure_ascii=False, indent=2))


def deserialize_project_doaps(
    shortcode: str,
    mode: Literal["original", "modified"],
) -> list[Doap]:
    """Deserialize the resource DOAPs from a JSON file."""
    filepath = _get_file_path(shortcode, mode)
    with open(filepath, mode="r", encoding="utf-8") as f:
        doaps_as_dict = json.load(f)
    doaps_as_dicts = doaps_as_dict.values()[0]
    return [Doap.model_validate(d) for d in doaps_as_dicts]
