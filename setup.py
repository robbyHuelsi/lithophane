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

long_description = Path("README.md").read_text(encoding="utf-8").splitlines()
gif_index = long_description.index("![Example Lithophane](https://raw.githubusercontent.com/robbyHuelsi/lithophane/main/result.gif)")
long_description[gif_index] = "[![Example Lithophane](https://raw.githubusercontent.com/robbyHuelsi/lithophane/main/result.tiff)](https://github.com/robbyHuelsi/lithophane/blob/main/result.gif)"
long_description = "\n".join(long_description)

required_packaged = Path("requirements.txt").read_text().splitlines()

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
    keywords=metadata.__keywords__,
    classifiers=metadata.__classifiers__,
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=metadata.__python_requires__,
    install_requires=required_packaged,
    scripts=["bin/lithophane"],
)
