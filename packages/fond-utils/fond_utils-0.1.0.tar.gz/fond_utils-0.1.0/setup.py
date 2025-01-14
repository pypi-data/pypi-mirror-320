import setuptools

import os

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, "fondutils", "__version__.py"), "r") as f:
    exec(f.read(), about)

with open("README.md", "r") as fh:
    long_description = fh.read()
    long_description = long_description.replace("> [!IMPORTANT]", "### IMPORTANT")
    long_description = long_description.replace("> [!TIP]", "### TIP")
    long_description = long_description.replace("> [!NOTE]", "### NOTE")

setuptools.setup(
    name=about["__title__"],
    description=about["__description__"],
    version=about["__version__"],
    author=about["__author__"],
    url=about["__url__"],
    author_email=about["__author_email__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=about["__license__"],
    packages=["fondutils", "fondutils.pddl", "fondutils.helpers"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    install_requires=["pddl"],
    entry_points={
        "console_scripts": ["fond-utils=fondutils.__main__:main"],
    },
    zip_safe=False,
)
