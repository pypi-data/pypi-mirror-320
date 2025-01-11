import io
import zipfile
from pathlib import Path
from typing import Tuple

import requests
from tqdm import tqdm

from ramonak import PACKAGES_PATH
from ramonak.packages.nexus import PACKAGES


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


def package_exists(package_name: str) -> bool:
    package_dir = package_path(package_name)

    if package_dir.exists() and any(package_dir.iterdir()):
        return True
    else:
        return False


def package_basic_info(package: str) -> Tuple[str, str, str]:
    package_version = ""
    package_name = ""
    package_author = ""

    if package.count("/") == 2:
        package_author, package_name, package_version = package.split("/")
    elif package.count("/") == 1:
        package_author, package_name = package.split("/")
        package_version = sorted(
            PACKAGES[package_author][package_name].items(),
            key=lambda x: x[0],
            reverse=True,
        )[0][0]
    else:
        raise Exception(
            "Wrong package name. At least author and package name must be present"
        )

    return package_author, package_name, package_version


def require(wished_package: str) -> None:
    print(f"Required {wished_package}...", end=" ")

    if package_exists(wished_package):
        print("OK")
        return
    else:
        print("Downloading...")

    package_author, package_name, package_version = package_basic_info(wished_package)

    file_url = PACKAGES[package_author][package_name][package_version]

    fetch_unzip(
        file_url,
        Path(PACKAGES_PATH, package_author, package_name, str(package_version)),
    )

    print(
        f"The package '{package_author}/{package_name}/{package_version}' has been installed successfully"
    )


def package_path(package_name: str) -> Path:
    return Path(PACKAGES_PATH, *(str(i) for i in package_basic_info(package_name)))
