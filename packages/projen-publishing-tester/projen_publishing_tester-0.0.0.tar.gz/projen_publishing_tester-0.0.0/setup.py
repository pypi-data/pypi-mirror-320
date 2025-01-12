import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "projen-publishing-tester",
    "version": "0.0.0",
    "description": "projen-publishing-tester",
    "license": "Apache-2.0",
    "url": "https://github.com/user/projen-publishing-tester.git",
    "long_description_content_type": "text/markdown",
    "author": "user<user@domain.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/user/projen-publishing-tester.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "projen_publishing_tester",
        "projen_publishing_tester._jsii"
    ],
    "package_data": {
        "projen_publishing_tester._jsii": [
            "projen-publishing-tester@0.0.0.jsii.tgz"
        ],
        "projen_publishing_tester": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "jsii>=1.106.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
