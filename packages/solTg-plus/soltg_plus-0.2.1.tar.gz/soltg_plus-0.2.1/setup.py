from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt', 'r') as req:
        return req.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='solTg-plus',
    python_requires='>3.5.2',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,  # This tells setuptools to include files listed in MANIFEST.in
    author = "Konstantin Britikov",
    author_email = "BritikovKI@Gmail.com",
    description = "Test generation for Solidity in Foundry format (https://github.com/foundry-rs/foundry).",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/zuru-zuru/soltgbackend",
    license = "GPL-3.0-only",
    
    # If needed, specify explicit paths
    install_requires=read_requirements(),
    package_data={
        'my_package': ['./deps/*'],
    },
    # Or for distribution-wide resources
    data_files=[('deps', ['deps/tgnonlin', 'deps/solc'])],
    entry_points={
        'console_scripts': [
            'solTg-plus=solTg.RunAll:main',
        ],
    },
)
