import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    'gunicorn>=19.7.1',
    'plotly>=2.0.9',
    'dash>=0.17.4',
    'dash-renderer>=0.7.2',
    'dash-html-components>=0.6.0',
    'dash-core-components>=0.5.0',
    'dash_daq>=0.5.0',
    'dash_bootstrap_components==0.10.0',
    'dash_admin_components==0.1.4',
    'score-component==0.4.9',
    'pretty_midi==0.2.9',
    'librosa==0.7.2',
    'visdcc==0.0.40',
    'music21==5.1.0'
]

setuptools.setup(
    name="orchestration-analyzer", # Replace with your own username
    version="0.5",
    author="Uljas Pulkkis",
    author_email="uljas.pulkkis@gmail.com",
    license='MIT',
    description="An orchestration analysis tool for composers, conductors, musicians and music theorists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/upulkkis/orchestration-analyzer",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	scripts=['bin.app'],
    entry_points={
    'console_scripts': ['orchan=bin.app:server'],
    },
    python_requires='>=3.7.6',
)