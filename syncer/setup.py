import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="syncer",
    version="0.0.1",
    author="Max Buck",
    author_email="maxwellhigginsbuck@gmail.com",
    description="Internal syncer app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://earbud.club",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

