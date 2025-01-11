from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sonnet-audio",
    version="1.0a1",
    author="Alfa Ozaltin",
    author_email="alfa.ozaltin@gmail.com",
    description="SONNET: Sound Network Negotiated Encoding Transmitter - Audio data transmission over sound",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alfaoz/sonnet",
    project_urls={
        "Bug Tracker": "https://github.com/alfaoz/sonnet/issues",
        "Documentation": "https://github.com/alfaoz/sonnet#readme",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Communications",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "sonnet"},
    packages=find_packages(where="sonnet"),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.7.0",
        "pyaudio>=0.2.11",
        "colorama>=0.4.4",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
)