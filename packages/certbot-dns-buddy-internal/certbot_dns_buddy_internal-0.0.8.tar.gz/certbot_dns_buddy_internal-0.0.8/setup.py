from setuptools import setup
from setuptools import find_packages
from os import path

version = "0.0.8"

install_requires = [
    "certbot>=0.31.0",
    "setuptools",
    "requests",
    "requests-mock",
    "idna",
]

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.rst")) as f:
    long_description = f.read()

setup(
    name="certbot-dns-buddy-internal",
    version=version,
    description="Buddy DNS internal Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/buddy/certbot-dns-internal",
    author="Michal Hankus",
    license="Apache License 2.0",
    python_requires=">=3.5.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "certbot.plugins": [
            "dns-buddy-internal = certbot_dns_buddy_internal.dns_internal:Authenticator"
        ]
    },
    test_suite="certbot_dns_buddy_internal",
)
