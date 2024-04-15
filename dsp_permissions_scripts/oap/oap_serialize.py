import itertools
import re
from pathlib import Path
from typing import Literal

from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_model import ValueOap
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
    logger.info(f"Writing {len(oaps)} OAPs into {str(folder)}")
    counter = 0
    for oap in oaps:
        if oap.resource_oap:
            _serialize_oap(oap.resource_oap, folder)
            counter += 1
        for value_oap in oap.value_oaps:
            _serialize_oap(value_oap, folder)
            counter += 1
    logger.info(f"Successfully wrote {len(oaps)} OAPs into {counter} files in folder {str(folder)}")


def _serialize_oap(oap: ResourceOap | ValueOap, folder: Path) -> None:
    iri = oap.resource_iri if isinstance(oap, ResourceOap) else oap.value_iri
    filename = re.sub(r"http://rdfh\.ch/[^/]+/", "resource_", iri)
    filename = re.sub(r"/", "_", filename)
    with open(folder / f"{filename}.json", mode="w", encoding="utf-8") as f:
        f.write(oap.model_dump_json(indent=2))


def deserialize_oaps(
    shortcode: str,
    mode: Literal["original", "modified"],
) -> list[ResourceOap]:
    """Deserialize the OAPs from JSON files."""
    folder = _get_project_data_path(shortcode, mode)
    res_oaps: list[ResourceOap] = []
    val_oaps: list[ValueOap] = []
    for file in folder.glob("**/*.json"):
        content = file.read_text(encoding="utf-8")
        val_oaps = []
        if "_values_" in file.name:
            val_oaps.append(ValueOap.model_validate_json(content))
        else:
            res_oaps.append(ResourceOap.model_validate_json(content))
    
    oaps = []
    for res_iri, val_oaps in itertools.groupby(val_oaps, key=lambda x: x.resource_iri):
        res_oap = next(filter(lambda x: x.resource_iri == res_iri, res_oaps))
        oaps.append(Oap(resource_oap=res_oap, value_oaps=val_oaps))
    return oaps
