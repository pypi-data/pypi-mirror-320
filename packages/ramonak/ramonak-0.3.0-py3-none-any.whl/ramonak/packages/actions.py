from pathlib import Path

from ramonak import PACKAGES_PATH
from ramonak.packages.utils import (
    fetch_unzip,
    get_package_exact_id_parts,
    package_exists,
    retrieve_package_url,
)


def require(wished_package: str) -> None:
    package_author, package_name, package_version = get_package_exact_id_parts(
        wished_package
    )

    package_path = Path(
        PACKAGES_PATH, package_author, package_name, str(package_version)
    )

    print(f"Required package '{wished_package}'...", end=" ")

    if package_exists(wished_package):
        print("OK")
        return package_path
    else:
        print("Downloading...")

    file_url = retrieve_package_url(package_author, package_name, package_version)

    fetch_unzip(
        file_url,
        package_path,
    )

    print(
        f"The package '{package_author}/{package_name}/{package_version}' has been installed successfully"
    )

    return package_path
