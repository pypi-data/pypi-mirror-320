# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libnumerixpy', 'libnumerixpy.math']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'libnumerixpy',
    'version': '0.1.1',
    'description': 'A Powerful Python/C Library for High-Performance Numerical Computing',
    'long_description': '# libnumerixpy\n\n<p align="center">A Powerful Python/C Library for High-Performance Numerical Computing</p>\n<br>\n<p align="center">\n\t<img src="https://img.shields.io/github/languages/top/alexeev-prog/libnumerixpy?style=for-the-badge">\n\t<img src="https://img.shields.io/github/languages/count/alexeev-prog/libnumerixpy?style=for-the-badge">\n\t<img src="https://img.shields.io/github/license/alexeev-prog/libnumerixpy?style=for-the-badge">\n\t<img src="https://img.shields.io/github/stars/alexeev-prog/libnumerixpy?style=for-the-badge">\n\t<img src="https://img.shields.io/github/issues/alexeev-prog/libnumerixpy?style=for-the-badge">\n\t<img src="https://img.shields.io/github/last-commit/alexeev-prog/libnumerixpy?style=for-the-badge">\n</p>\n\n> [!CAUTION]\n> At the moment, libnumerixpy is under active development (alpha), many things may not work, and this version is not recommended for use (all at your own risk).\n\nlibnumerixpy is a powerful, cross-platofrm Python/C library designed for high-performance numerical computing in the domains of physics, mathematics, and computer science.\n\nLibnumerixpy use Python/C API!\n\nYou can join to our [small russian telegram blog](https://t.me/hex_warehouse).\n\n## Key Features\n - **Extensive Functionality**: libnumerixpy provides a wide range of functions coverint the core areas of mathematics, physics, and computer science, including:\n  - Mathematics: linear algebra, calculus, geometry\n  - Physics: kinematics, mechanics, thermodynamics, electronics\n  - Computer Science: algorithms, numerical methods, data processing\n - **High Performance**: The library is optimized for maximum performance, leveraging modern techniques such as parallel computing and vectorization\n - **Cross-platform Support**: libnumerixpy supports major operating systems (Windows, Linux, macOS).\n - **Ease of Use**: A simple and intuitive API, comprehensive documentation, and numerous examples facilitate the integration of the library into your projects.\n - **Modular Architecture**: libnumerixpy is designed with a modular structure, allowing selective compilation of only the required components.\n - **Extensibility**: The library is open to the developer community, who can contribute improvements and additions.\n\n## Architecture\nlibnumerixpy has a modular architecture consisting of the following core components:\n\n - core: Provides essential data types, error handling functions, and utility tools.\n - mathematics: Implements algorithms for linear algebra, calculus, and geometry.\n - physics: Offers functions for solving problems in the areas of kinematics, mechanics, thermodynamics and electronics.\n\nEach module has its own set of header files and source files, ensuring flexibility and the ability to selectively compile the required parts of the library.\n\n## Credits for C/Python API\n\n + [C/Python API Official Docs](https://docs.python.org/3/c-api)\n + [Enhancing python with custom C extensions](https://stackabuse.com/enhancing-python-with-custom-c-extensions/)\n + [dm-fedorov/python-modules](https://github.com/dm-fedorov/python-modules/blob/master/c-api.md)\n + [Жажда скорости: Python с расширениями C](https://nuancesprog.ru/p/14010/)\n\n## Copyright\nlibnumerixpy is released under the [GNU LGPL 2.1](https://github.com/alexeev-prog/libnumerixpy/blob/main/LICENSE).\n\nCopyright © 2024 Alexeev Bronislav. All rights reversed.\n\n',
    'author': 'alexeev-prog',
    'author_email': 'alexeev.dev@mail.ru',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
