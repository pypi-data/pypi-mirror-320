from setuptools import setup, find_packages

setup(
    name="bonjourlowbackk",
    version="0.1.0",
    author="Marco",
    author_email="m.figueiredo367@gmail.com",
    description="Test pour lowbackk",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LowBackk/Package-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
