"""Utility methods"""

from __future__ import annotations

import datetime as dt
from typing import Dict, Optional

from packaging import version

from .model import RointeProduct

DEFAULT_TIME_ZONE: dt.tzinfo = dt.timezone.utc


def now(time_zone: Optional[dt.tzinfo] = None) -> dt.datetime:
    """Get now in specified time zone."""
    return dt.datetime.now(time_zone or DEFAULT_TIME_ZONE)


def find_max_fw_version(data: Dict, device_class: str, product_version: str) -> str | None:
    """Finds the latest FW version for a specific device class and version"""

    if device_class in data:
        if (
            product_version in data[device_class]
            and "end_user" in data[device_class][product_version]
        ):
            root = data[device_class][product_version]["end_user"]

            max_version = None

            for entry in root:
                ptr = version.parse(entry)
                if max_version is None or ptr > max_version:
                    max_version = ptr

            return str(max_version)

    return None


def build_update_map(firmware_data: dict) -> dict[RointeProduct, Optional[dict[str, str]]]:
    """
    Builds an update map for each device.

    Output is a dict of [product, [existing_version, target_version]

    Where [target_version] is the next version the product can be updated to.
    and [existing_verion] is the product's current version.
    """
    fw_map: dict[RointeProduct, Optional[dict[str, str]]] = {}

    for entry in RointeProduct:
        fw_map[entry] = build_product_fw_map(entry, firmware_data)

    return fw_map


def build_product_fw_map(product: RointeProduct, firmware_data: dict) -> Optional[dict[str, str]]:
    """Builds the upgrade map for a specific product."""

    if product.device_type not in firmware_data:
        return None

    root_node = firmware_data[product.device_type]

    if product.version not in root_node:
        return None

    product_versions = root_node[product.version]["end_user"]

    upgrade_map = {}

    for version_entry in product_versions:
        new_version = product_versions[version_entry].get("firmware_new_version", None)

        if new_version:
            upgrade_map[version_entry] = new_version

    return upgrade_map


def get_product_by_type_version(
    product_type: str, product_version: str
) -> RointeProduct | None:
    """Find the product model by its type and version."""

    for entry in RointeProduct:
        if entry.device_type == product_type and entry.version == product_version:
            return entry

    return None
