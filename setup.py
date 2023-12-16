import setuptools
from pathlib import Path

import importlib.util


def import_from_path(path):
    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


metadata = import_from_path(
    Path(__file__).parent / "src" / "lithophane" / "metadata.py"
)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required_packaged = f.read().splitlines()

setuptools.setup(
    name=metadata.__project_name__,
    version=metadata.__version__,
    author=metadata.__author__,
    author_email=metadata.__email__,
    license=metadata.__license__,
    description=metadata.__doc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=metadata.__url__,
    download_url=f"{metadata.__url__}/archive/v_{metadata.__version__}.tar.gz",
    keywords=metadata.__keywords__,
    classifiers=metadata.__classifiers__,
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=metadata.__python_requires__,
    install_requires=required_packaged,
)
