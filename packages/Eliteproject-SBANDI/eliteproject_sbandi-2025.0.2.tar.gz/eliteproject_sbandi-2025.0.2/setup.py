import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="Eliteproject-SBANDI",
    version="2025.0.2",
    author="Stefano Bandini",
    author_email="stefano.bandini@email.it",
    description="OEC ELITE LOG PARSER",
    long_description="Parse a compressed log  file from OEC ELITE Equipment, now can select file to parse",
    long_description_content_type="text/markdown",
    url="https://github.com/users/Egorroico/projects/1/views/1",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)