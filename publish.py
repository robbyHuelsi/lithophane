import re
import subprocess
from datetime import date
from pathlib import Path


def update_metadata(source_code_file_path: Path, start_year: int = None) -> str:
    """
    Update metadata in source code file.

    Args:
        source_code_file_path (Path): Path to source code file
        start_year (int, optional): Start year of project. Defaults to None. If None, copyright will not be updated.

    Returns:
        str: Next version

    Raises:
        Exception: If version is not found
        Exception: If author is not found
        Exception: If author is not found
    """

    # Load source code
    source_code = source_code_file_path.read_text()

    # Find version
    version_regexp = re.compile(r"__version__ ?= ?[\"'](?P<version>.*)[\"']")
    sub_ver_regexp = re.compile(r"[0-9]+")
    version = version_regexp.search(source_code)
    if not version:
        raise Exception(f'Version not found in file "{source_code_file_path}"')
    version = version.groupdict()["version"].split(".")

    # Get next version from user
    next_sub_ver_sug = sub_ver_regexp.search(version[-1])
    if next_sub_ver_sug is not None:
        next_sub_ver_sug = str(int(next_sub_ver_sug[0]) + 1)
    else:
        next_sub_ver_sug = version[-1]
    next_ver_suggestion = ".".join(version[:-1] + [next_sub_ver_sug])
    next_version = input(f"New Version [{next_ver_suggestion}]: ")
    next_version = next_version if next_version else next_ver_suggestion

    # Replace version in source code
    source_code = version_regexp.sub(f'__version__ = "{next_version}"', source_code)

    # Update copyrigth if start_year is not None
    if start_year is not None:
        # Find copyright
        copyright_regexp = re.compile(r"__copyright__ ?= ?[\"'](?P<copyright>.*)[\"']")
        if not copyright_regexp.search(source_code):
            raise Exception(f'Copyright not found in file "{source_code_file_path}"')

        # Find author
        author_regexp = re.compile(r"__author__ ?= ?[\"'](?P<author>.*)[\"']")
        author = author_regexp.search(source_code)
        if not author:
            raise Exception(f'Author not found in file "{source_code_file_path}"')
        author = author.groupdict()["author"]

        # Update copyright in source code
        current_year = date.today().year
        if current_year == start_year:
            years = str(start_year)
        else:
            years = f"{start_year}-{current_year}"
        source_code = copyright_regexp.sub(
            f'__copyright__ = "Copyright (c) {years} {author}. All Rights Reserved."',
            source_code,
        )

    # Save source code
    source_code_file_path.write_text(source_code)

    return next_version


def update_requirements(
    requirements_file_path: Path, package_path: Path, pin_mode: str = None
):
    """
    Update requirements file.

    Args:
        requirements_file_path (Path): Path to requirements file
        package_path (Path): Path to package
        pin_mode (str, optional): if not None, it enables dynamic versioning. Defaults to None. Can be "compat", "gt", "no-pin".
    """

    print()
    print("Prepare...")
    for package in ["pipreqs", "build"]:
        subprocess.run(
            ["python3", "-m", "pip", "install", "--upgrade", package], check=True
        )

    print()
    print(f"Update {requirements_file_path}...")
    pipreqs_args = [
        "pipreqs",
        "--force",
        "--savepath",
        requirements_file_path,
        package_path.parent,
    ]
    if pin_mode:
        pipreqs_args += ["--mode", pin_mode]
    subprocess.run(pipreqs_args, check=True)


def generate_module(package_name: str, start_year: int = None, pin_mode: str = None):
    """
    Generate module.

    Args:
        package_name (str): Name of package
        start_year (int): Start year of project. If None, copyright will not be updated.
        pin_mode (str, optional): if not None, it enables dynamic versioning. Defaults to None. Can be "compat", "gt", "no-pin".
    """

    package_path = Path(__file__).parent / "src" / package_name

    # Update metadata
    version = update_metadata(
        source_code_file_path=package_path / "metadata.py",
        start_year=start_year,
    )

    # Update requirements
    requirements_file_path = Path(__file__).parent / "requirements.txt"
    # update_requirements(
    #     requirements_file_path=requirements_file_path,
    #     package_path=package_path,
    #     pin_mode=pin_mode,
    # )

    print()
    print("Build...")
    subprocess.run(["python3", "-m", "build", Path(__file__).parent], check=True)

    print()
    print("Git commit, tag, push...")
    subprocess.run(
        f"git add {package_path} {requirements_file_path}", shell=True, check=True
    )
    subprocess.run(
        f'git commit {package_path} {requirements_file_path} -m "Version {version}"',
        shell=True,
        check=True,
    )
    subprocess.run(
        f'git tag -a "v{version}" -m "Version {version}"', shell=True, check=True
    )
    subprocess.run("git tag -d latest", shell=True, check=False)
    subprocess.run("git push --delete origin latest", shell=True, check=False)
    subprocess.run(f'git tag -a latest -m "Version {version}"', shell=True, check=True)
    subprocess.run("git push && git push --tags", shell=True, check=True)

    # print()
    # print("Upload...")
    # subprocess.run(
    #     f"python -m twine upload --repository github-{package_name} dist/{package_name}-{version}* --verbose"
    # )


if __name__ == "__main__":
    generate_module(
        package_name="lithophane",
        start_year=None,  # Copyright should not be updated
        pin_mode="no-pin",
    )
