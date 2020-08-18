import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="orchestration-analyzer", # Replace with your own username
    version="0.5",
    author="Uljas Pulkkis",
    author_email="uljas.pulkkis@gmail.com",
    description="An orchestration analysis tool for composers, conductors, musicians and music theorists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/upulkkis/orchestration-analyzer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	scripts=['bin.app'],
    python_requires='>=3.7.6',
)