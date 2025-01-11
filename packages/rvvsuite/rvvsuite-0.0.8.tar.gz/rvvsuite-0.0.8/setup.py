import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "rvvsuite",
    version = "0.0.8",
    author = "Nguyen Binh Khiem",
    author_email = "khiemnb153@gmail.com",
    description = "A set of tools for developing RISC-V Vector IP includes Random Test Generator (RTG), Assembler, and Simulator",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url='https://github.com/khiemnb153/rvvsuite',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.13"
)