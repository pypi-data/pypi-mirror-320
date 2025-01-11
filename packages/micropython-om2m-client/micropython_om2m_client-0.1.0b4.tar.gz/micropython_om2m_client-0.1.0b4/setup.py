from setuptools import setup, find_packages

setup(
    name="micropython-om2m-client",
    version="0.1.0b4",
    description="A MicroPython client for interacting with OM2M CSE (Work in Progress).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ahmad Hammad, Omar Hourani",
    author_email="ahmadhammad.uca@gmail.com, omar.hourani@ieee.org",
    url="https://github.com/SCRCE/micropython-om2m-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: Implementation :: MicroPython",
    ],
    install_requires=[
    ],
)
