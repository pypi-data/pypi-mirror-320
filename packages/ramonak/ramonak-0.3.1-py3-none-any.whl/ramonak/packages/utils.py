import io
import re
import zipfile
from pathlib import Path
from typing import Tuple

import requests
import tomllib
from tqdm import tqdm

from ramonak import PACKAGES_PATH
from ramonak.packages import NEXUS_PATH


def fetch_unzip(zip_file_url: str, destination_dir: str) -> Path:
    Path(destination_dir).mkdir(exist_ok=True, parents=True)
    bio = io.BytesIO()

    response = requests.get(zip_file_url, stream=True)
    with tqdm.wrapattr(
        bio,
        "write",
        miniters=1,
        desc=zip_file_url.split("/")[-1],
        total=int(response.headers.get("content-length", 0)),
    ) as fout:
        for chunk in response.iter_content(chunk_size=4096):
            fout.write(chunk)

    z = zipfile.ZipFile(bio)
    z.extractall(destination_dir)


def package_path(package_id: str) -> Path:
    author, name, version = get_package_id_parts(package_id)
    return Path(PACKAGES_PATH, author, name, version)


def local_package_exists(package_name: str) -> bool:
    package_dir = package_path(package_name)

    if package_dir.exists() and any(package_dir.iterdir()):
        return True
    else:
        return False


def get_package_id_parts(package: str) -> Tuple[str, str, str]:
    package = re.sub(r"\s", "", package)

    package_version = ""
    package_name = ""
    package_author = ""

    if "==" in package:  # Installing exact version
        _, package_version = package.split("==")
        package_author, package_name = package.split("==")[0].split("/")
    elif package.count("/") == 1:  # Get latest version
        package_author, package_name = package.split("/")
    else:
        raise Exception(
            "Wrong package name. At least author and package name must be present"
        )

    return package_author, package_name, package_version


def get_package_versions(package_author, package_name) -> list:
    package_file = str(Path(NEXUS_PATH, package_author, package_name)) + ".toml"
    package_dict = tomllib.loads(open(package_file, "r", encoding="utf8").read())

    return package_dict["versions"]


def retrieve_package_url(package_author, package_name, package_version) -> str:
    package_file = str(Path(NEXUS_PATH, package_author, package_name)) + ".toml"
    package_dict = tomllib.loads(open(package_file, "r", encoding="utf8").read())

    for version in package_dict["versions"]:
        if version["id"] == package_version:
            return version["url"]

    raise Exception(
        "No such package version found: {}/{}=={}".format(
            package_author, package_name, package_version
        )
    )
