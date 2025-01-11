from setuptools import setup

libs = open("requirements.txt").read().splitlines()
setup(
    name="nm25",
    license="MIT",
    platforms=["any"],
    install_requires=libs,
    package_data={
        "nm25": ["data/*/*.md"],
    },
)
