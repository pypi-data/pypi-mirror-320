# Copyright (C) 2021 The InstanceLib Authors. All Rights Reserved.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import pathlib
import setuptools  # type: ignore

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(  # type: ignore
    name="instancelib",
    version="0.5.2",  # NOSONAR
    description="A generic interface for datasets and Machine Learning models",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Michiel Bron",
    author_email="m.p.bron@uu.nl",
    license="GNU LGPL v3",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    package_data={"instancelib": ["py.typed"]},
    packages=setuptools.find_packages(),  # type: ignore
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pandas",
        "h5py",
        "scikit-learn",
        "openpyxl",
        "xlrd",
        "tqdm",
        "more-itertools",
        "typing_extensions",
    ],
    extras_require={
        "doc2vec": ["gensim"],
        "hdf5": ["tables"],
    },
)
