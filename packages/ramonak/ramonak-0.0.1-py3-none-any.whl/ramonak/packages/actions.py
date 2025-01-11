import io
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

from ramonak import PACKAGES_PATH


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
    package_dir = Path(PACKAGES_PATH, *package_name.split("/"))

    if package_dir.exists() and any(package_dir.iterdir()):
        return True
    else:
        return False


def require(package_name: str) -> None:
    print(f"Required {package_name}...", end=" ")

    if package_exists(package_name):
        print("Package exists, skipping")
        return
    else:
        print("Downloading...")

    if package_name == "@bnkorpus/grammar_db/20230920":
        fetch_unzip(
            "https://github.com/Belarus/GrammarDB/releases/download/RELEASE-202309/RELEASE-20230920.zip",
            Path(PACKAGES_PATH, package_name),
        )
    else:
        print("Unknown package. Stopping...")
        return

    print("OK")


def package_path(package_name: str) -> str:
    return Path(PACKAGES_PATH, package_name)
