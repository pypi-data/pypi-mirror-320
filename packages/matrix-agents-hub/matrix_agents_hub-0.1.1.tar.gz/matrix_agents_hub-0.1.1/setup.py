from setuptools import setup, find_packages
import os

# 读取 README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取 requirements.txt
requirements = [
    "requests>=2.25.0",
    "python-dotenv>=0.19.0",
    "colorlog>=6.7.0"
]

# 如果 requirements.txt 存在，则从文件读取
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="matrix-agents-hub",
    version="0.1.1",
    author="Ray Xie",
    author_email="xie.xinfa@gmail.com",
    description="A hub for managing AI agents",
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
    install_requires=requirements,
) 