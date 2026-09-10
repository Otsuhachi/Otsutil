import re
from pathlib import Path

from setuptools import find_packages, setup

pd_this = Path(__file__).parent
long_description = (pd_this / "README.md").read_text(encoding="utf-8")

version = None
with (pd_this / "otsutil/__init__.py").open("r", encoding="utf-8") as f:
    for line in (x.rstrip("\n") for x in f):
        if (find := re.fullmatch(r'^__VERSION__ = "([^"]+)"', line)) is None:
            continue

        version = find.groups()[0].strip()

if version is None:
    msg = "`otsutil`バージョン情報の取得に失敗しました。"
    raise ValueError(msg)

setup(
    name="otsutil",
    version=version,
    description="A general-purpose utility package using Python 3.12+ features.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Otsuhachi",
    author_email="agequodagis.tufuiegoeris@gmail.com",
    license="MIT License",
    python_requires=">=3.12",
    packages=find_packages(where=".", include=["otsutil*"]),
    package_data={
        "otsutil": ["py.typed"],
    },
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
