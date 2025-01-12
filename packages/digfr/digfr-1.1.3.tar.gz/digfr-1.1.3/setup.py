from setuptools import setup, find_packages

setup(
    name = "digfr",
    version = "1.1.3",
    packages = find_packages(),
    description = "Dig Finacial Report Infomation",
    install_requires=[
        'requests',
        'pandas',
    ],
    author = "Tommy",
    url = "https://digfr.info/digfrlib/"
)