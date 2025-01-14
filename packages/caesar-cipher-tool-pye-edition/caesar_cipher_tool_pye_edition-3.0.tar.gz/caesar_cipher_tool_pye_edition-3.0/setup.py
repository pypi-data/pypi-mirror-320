from setuptools import setup, find_packages

VERSION = '3.0'
DESCRIPTION = 'A simple terminal program use to encipher/decipher text to/from Caesar Cipher.'
with open("readme.md") as file:
    LONG_DESCRIPTION = file.read()

setup(
    name = "caesar_cipher_tool_pye_edition",
    version = VERSION,
    author = "Zizel",
    author_email = "danbua999@gmail.com",
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    long_description_content_type = "text/markdown",
    url = "https://github.com/uwungu01-rep/caesar-cipher-tool-python.edition",
    packages = find_packages(),
    install_requires = [], # add any additional packages that 
    # needs to be installed along with your package. Eg: 'caer'
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points = {
        'console_scripts': [
            'cct  = caesar_cipher_tool_pye_edition.main:main',
        ],
    },
)
