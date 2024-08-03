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
    value_oap_count = sum(len(oap.value_oaps) for oap in oaps)
    logger.info(f"Writing {len(oaps)} resource OAPs and {value_oap_count} value OAPs into {folder}")
    for oap in oaps:
        _serialize_oap(oap.resource_oap, folder)
        for value_oap in oap.value_oaps:
            _serialize_oap(value_oap, folder)
    logger.info(f"Successfully wrote {len(oaps)} resource OAPs and {value_oap_count} value OAPs into folder {folder}")


def _serialize_oap(oap: ResourceOap | ValueOap, folder: Path) -> None:
    iri = oap.resource_iri if isinstance(oap, ResourceOap) else oap.value_iri
    filename = re.sub(r"http://rdfh\.ch/[^/]+/", "resource_", iri)
    filename = re.sub(r"/", "_", filename)
    Path(folder / f"{filename}.json").write_text(oap.model_dump_json(indent=2), encoding="utf-8")


def deserialize_oaps(
    shortcode: str,
    mode: Literal["original", "modified"],
) -> list[Oap]:
    """Deserialize the OAPs from JSON files."""
    res_oaps, val_oaps = _read_all_oaps_from_files(shortcode, mode)
    oaps = _group_oaps_together(res_oaps, val_oaps)
    return oaps


def _read_all_oaps_from_files(
    shortcode: str, mode: Literal["original", "modified"]
) -> tuple[list[ResourceOap], list[ValueOap]]:
    folder = _get_project_data_path(shortcode, mode)
    res_oaps: list[ResourceOap] = []
    val_oaps: list[ValueOap] = []
    all_files = list(folder.glob("**/*.json"))
    for file in all_files:
        content = file.read_text(encoding="utf-8")
        if "_values_" in file.name:
            val_oaps.append(ValueOap.model_validate_json(content))
        else:
            res_oaps.append(ResourceOap.model_validate_json(content))
    logger.info(f"Read {len(res_oaps)} resource OAPs and {len(val_oaps)} value OAPs from {len(all_files)} files")
    return res_oaps, val_oaps


def _group_oaps_together(res_oaps: list[ResourceOap], val_oaps: list[ValueOap]) -> list[Oap]:
    oaps: list[Oap] = []
    deserialized_resource_iris = []

    def sort_algo(x: ValueOap) -> str:
        """
        According to https://docs.python.org/3/library/itertools.html#itertools.groupby,
        the iterable must be sorted on the same key function, before passing it to itertools.groupby().
        """
        return x.resource_iri

    for res_iri, _val_oaps in itertools.groupby(sorted(val_oaps, key=sort_algo), key=sort_algo):
        res_oap = next(x for x in res_oaps if x.resource_iri == res_iri)
        oaps.append(Oap(resource_oap=res_oap, value_oaps=sorted(_val_oaps, key=lambda x: x.value_iri)))
        deserialized_resource_iris.append(res_iri)

    remaining_res_oaps = [oap for oap in res_oaps if oap.resource_iri not in deserialized_resource_iris]
    oaps.extend(Oap(resource_oap=res_oap, value_oaps=[]) for res_oap in remaining_res_oaps)

    oaps.sort(key=lambda oap: oap.resource_oap.resource_iri)
    logger.debug(f"Grouped {len(res_oaps)} resource OAPs and {len(val_oaps)} value OAPs into {len(oaps)} OAPs")
    return oaps
