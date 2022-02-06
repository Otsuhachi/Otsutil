import sys

from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()
with open('LICENSE.txt', 'r', encoding='utf-8') as f:
    lcs = f.read()
info = sys.version_info
setup(
    name='otsutil',
    version='2022.2.7',
    url='https://github.com/Otsuhachi/Otsutil',
    description='よく使う関数、クラスを纏めたライブラリ',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='Otsuhachi',
    author_email='agequodagis.tufuiegoeris@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Natural Language :: Japanese',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'License :: OSI Approved :: MIT License',
    ],
    license=lcs,
    keywords='Python ObjectSaver deduplicate load_json read_lines save_json setup_path write_lines',
)
