import shutil
from pathlib import Path
from typing import Union

import tomllib

from ramonak import PACKAGES_PATH
from ramonak.packages import NEXUS_PATH
from ramonak.packages.utils import (
    fetch_unzip,
    get_package_id_parts,
    get_package_versions,
    local_package_exists,
    retrieve_package_url,
)


def require(package_id: str) -> Path:
    package_author, package_name, package_version = get_package_id_parts(package_id)

    if "==" not in package_id:
        package_version = get_package_versions(package_author, package_name)[-1]["id"]
        print(
            f"Required '{package_id}=={package_version}'...",
            end=" ",
        )
    else:
        print(f"Required package '{package_id}'...", end=" ")

    package_path = Path(
        PACKAGES_PATH, package_author, package_name, str(package_version)
    )

    if local_package_exists(package_id):
        print("Already satisfied")
        return package_path
    else:
        print("Downloading...")

    file_url = retrieve_package_url(package_author, package_name, package_version)

    fetch_unzip(
        file_url,
        package_path,
    )

    print(
        f"The package '{package_author}/{package_name}=={package_version}' has been installed successfully"
    )

    return package_path


def remove(package_id: str):
    removable_path = ""

    author, name, version = get_package_id_parts(package_id)

    if "==" not in package_id:
        print(
            "Removing the local metapackage '{}/{}'...".format(author, name),
            end=" ",
        )
        removable_path = Path(PACKAGES_PATH, author, name)
    else:
        print(
            "Removing the local package '{}/{}=={}'...".format(author, name, version),
            end=" ",
        )
        removable_path = Path(PACKAGES_PATH, author, name, version)

    try:
        shutil.rmtree(removable_path)
    except FileNotFoundError:
        raise Exception("The package doesn't exist in the local storage")
    else:
        print("OK")


def purge():
    print("Removing all the local packages...", end=" ")

    shutil.rmtree(PACKAGES_PATH)
    PACKAGES_PATH.mkdir(parents=True)

    print("OK")


def info(package_id) -> Union[str, dict]:
    author, name, version = get_package_id_parts(package_id)
    package_file = str(Path(NEXUS_PATH, author, name)) + ".toml"
    descriptor_text = open(package_file, "r", encoding="utf8").read()
    descriptor_data = tomllib.loads(descriptor_text)

    if not version:
        print("type", "=", "metapackage")
    else:
        print("type", "=", "package")

    for key, value in descriptor_data["package_info"].items():
        print(key, "=", value)

    if not version:
        versions = ",".join(v["id"] for v in descriptor_data["versions"])
        print(f"versions = [{versions}]")
    else:
        version = next(v for v in descriptor_data["versions"] if v["id"] == version)

        for key, value in version.items():
            print(f"version.{key} = {value}")
