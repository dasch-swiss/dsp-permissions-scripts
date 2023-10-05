import re
from pathlib import Path
from typing import Literal

from dsp_permissions_scripts.models.oap import Oap


def serialize_resource_oaps(
    resource_oaps: list[Oap],
    shortcode: str,
    mode=Literal["original", "modified"],
) -> None:
    """Serialize the resource OAPs to JSON files into the folder "OAPs_project_{shortcode}_{mode}"."""
    folder = Path(f"OAPs_project_{shortcode}_{mode}")
    folder.mkdir(exist_ok=True)
    for res_oap in resource_oaps:
        filename = re.sub(r"", "_", res_oap.object_iri)
        with open((folder / filename).with_suffix(".json"), mode="w", encoding="utf-8") as f:
            f.write(res_oap.model_dump_json())


def deserialize_resource_oaps(
    shortcode: str,
    mode: Literal["original", "modified"],
) -> list[Oap]:
    """Deserialize the resource OAPs from JSON files in the folder "OAPs_project_{shortcode}_{mode}"."""
    folder = Path(f"OAPs_project_{shortcode}_{mode}")
    resource_oaps = []
    for file in folder.iterdir():
        if file.suffix == ".json" and "rdfh" in file.name:
            with open(file, mode="r", encoding="utf-8") as f:
                resource_oaps.append(Oap.model_validate_json(f.read()))
    return resource_oaps
