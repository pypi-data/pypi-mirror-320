from setuptools import setup

libs = open("requirements.txt").read().splitlines()
setup(
    name="nm25",
    version="1.6",
    url="",
    license="MIT",
    author="",
    author_email="",
    platforms=["any"],
    install_requires=libs,
    package_data={
        "nm25": ["data/*/*.md"],
    },
)
