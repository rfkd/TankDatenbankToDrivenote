"""
    This file is part of Tank-Datenbank to Drivenote.

    Copyright (C) 2023 Ralf Dauberschmidt <ralf@dauberschmidt.de>

    Tank-Datenbank to Drivenote is free software; you can redistribute it and/or modify it under the terms of the GNU
    General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your
    option) any later version.

    Tank-Datenbank to Drivenote is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
    even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License along with Tank-Datenbank to Drivenote. If not,
    see <http://www.gnu.org/licenses/>.
"""

import argparse
import logging
import sys

from datetime import datetime
from pathlib import Path

from lxml import etree

# Define the logger
LOG = logging.getLogger(Path(__file__).stem)


def _parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    :return: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert a Tank-Datenbank XML export to Drivenote-compatible CSV files.")
    parser.add_argument("-i", "--in-file", help="Tank-Datenbank XML export", required=True)
    parser.add_argument("-o", "--out-directory", help="directory to save the converted exports in", default=".")

    arguments = parser.parse_args()

    if not Path(arguments.in_file).exists():
        parser.error(f"argument -i/--in-file: file '{arguments.in_file}' does not exist")
    if not Path(arguments.out_directory).is_dir():
        parser.error(
            f"argument -o/--out-directory: directory '{arguments.out_directory}' does not exist or is not a directory")

    return arguments


def _get_child(element: etree.Element, tag: str) -> str:
    """
    Get the value of a child element.
    :param element: Element to search in.
    :param tag: Tag of the child element.
    :return: Child value.
    """
    tags = element.xpath(tag)

    if len(tags) != 1:
        LOG.critical(f"Tank-Datenbank XML contains a vehicle with a wrong number of '{tag}'-tags.")
        sys.exit(1)

    return tags[0].text


def _convert(tank_datenbank_xml: Path, out_directory: Path):
    """
    Convert the given Tank-Datenbank XML export to a Drivenote-compatible CSV.
    :param tank_datenbank_xml: Path to the Tank-Datenbank XML export.
    :param out_directory: Directory to save the converted exports in.
    """
    vehicles = None
    try:
        vehicles = etree.parse(tank_datenbank_xml).getroot().xpath("//fueldb/vehicles/vehicle")
    except etree.XMLSyntaxError as error:
        LOG.critical(f"Tank-Datenbank XML '{tank_datenbank_xml}' syntax is invalid: {error}")
        sys.exit(1)
    LOG.info(f"Successfully parsed Tank-Datenbank '{tank_datenbank_xml}'.")

    for vehicle in vehicles:
        vehicle_name = _get_child(vehicle, "name")
        LOG.info(f"Processing vehicle '{vehicle_name}' ...")

        drivenote_refueling_logs = ["Date,Mileage,Price,Consumption,Partial"]
        for refueling in vehicle.xpath("refuelings/refueling"):
            date = datetime.fromtimestamp(float(_get_child(refueling, "tstamp")) / 1000).strftime("%d.%m.%Y")
            mileage = float(_get_child(refueling, "mileage"))
            price = float(_get_child(refueling, "price"))
            consumption = float(_get_child(refueling, "consumption"))
            try:
                partial = refueling.xpath("isPartial")[0].text
            except IndexError:
                partial = "0"

            drivenote_refueling_logs += [f"{date},{mileage},{price},{consumption},{partial}"]

        with open(out_directory / f"Drivenote_Refuelings_{vehicle_name.replace(' ', '_')}.csv", mode="w",
                  encoding="UTF-8") as file:
            for drivenote_log in drivenote_refueling_logs:
                file.write(f"{drivenote_log}\n")


def main():
    """
    Main entry point.
    """
    arguments = _parse_arguments()
    logging.basicConfig(format="[%(levelname).1s] %(message)s", level=logging.INFO)

    _convert(Path(arguments.in_file), Path(arguments.out_directory))


if __name__ == "__main__":
    main()
