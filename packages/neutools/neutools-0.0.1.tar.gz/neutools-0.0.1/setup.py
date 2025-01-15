# setup.py
from setuptools import setup, find_packages

setup(
    name='neutools',
    author="cxykevin",
    author_email="cxykevin@yeah.net",
    description="neutron panel debug tools",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://gitee.com/cxy_kevin/neutron",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.11',
    install_requires=["typer"],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'neutools = neutools.__main__:app',
        ],
    },
    version="0.0.1"
)
