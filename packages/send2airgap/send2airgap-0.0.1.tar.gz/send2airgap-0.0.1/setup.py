"""Python setup.py for send2airgap package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("send2airgap", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="send2airgap",
    version=read("send2airgap", "VERSION"),
    description="A Python package enabling the secure transfer of data from an insecure sender to an air-gapped computer equipped with a camera.",
    url="https://github.com/poing/Send2AirGap/",
    project_urls={
        'Documentation': 'https://poing.github.io/Send2AirGap',
        'Source': 'https://github.com/poing/Send2AirGap',
        'Bug Tracker': 'https://github.com/poing/Send2AirGap/issues/',
    },
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Brian LaVallee",
    author_email="brian.lavallee@invite-comm.jp",
	python_requires='>=3.13',
    keywords=[
        "air gap", 
        "air gapped", 
        "air gapping",
        "air wall", 
        "air-gap", 
        "air-gapping",
        "air-wall", 
        "airgap",
        "airgapped", 
        "airgapping",
        "airwall",
        "camera",
        "communication security",
        "communicationsecurity",
        "cybersecurity",
        "data transmission",
        "datatransfer",
        "disconnected network",
        "hardwaresecurity",
        "isolatednetwork",
        "network security",
        "networking",
        "networksecurity",
        "physically isolated",
        "qr-code",
        "qrcode",
        "receive data",
        "recvdata",
        "secure computer network",
        "securecomputing",
        "send data",
        "senddata",
    ],
	classifiers = [
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Intended Audience :: Information Technology",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3.13",
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'Topic :: Communications :: File Sharing',
        'Topic :: Communications',
        'Topic :: Security', 
        'Topic :: Utilities',
        "Natural Language :: English",
        "Operating System :: OS Independent",
	],
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["send2airgap = send2airgap.__main__:main"]
    },
    extras_require={"test": read_requirements("requirements-test.txt")},
)
