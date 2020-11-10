import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-package-djdenpa", # Replace with your own username
    version="0.0.1",
    author="Eugene",
    author_email="eugenexlin@gmail.com  ",
    description="lib to help make live2d avatar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eugenexlin/nice-face",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)