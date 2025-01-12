from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lightning_proxies",
    version="0.1.0",
    author="sanders basket",
    description="A Python client for managing Lightning Proxies API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lightning_proxies",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests>=2.25.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "flake8>=3.8",
        ],
    },
)