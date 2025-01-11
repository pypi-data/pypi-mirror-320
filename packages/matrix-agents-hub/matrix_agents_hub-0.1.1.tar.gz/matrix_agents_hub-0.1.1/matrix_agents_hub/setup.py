from setuptools import setup, find_packages

with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="matrix-agents-hub",
    version="0.1.1",
    author="Ray Xie",
    author_email="xie.xinfa@gmail.com",
    description="A hub for managing and interacting with various AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xray918/matrix",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "colorlog>=6.7.0",
    ],
) 