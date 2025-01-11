from setuptools import setup, find_packages

setup(
    name="depster",
    version="1.1.1",
    author="Simon H. Benzer",
    author_email="SimonHBenzer@gmail.com",
    description="A tool create a detailed CSV analyzing your project's dependencies",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shbenzer/depster",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "depster=depster.depster:main",  # CLI command as depster
        ],
    },
)
