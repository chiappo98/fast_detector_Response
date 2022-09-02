#
# Copyright 2020-2022 N. Tosi, V. Pia <nicolo.tosi@bo.infn.it>
#
# This program is free software:
# you can redistribute it and/or modify it under the terms of the GNU
# Lesser General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='drdf',  # Required
    version='0.1.0',  # Required
    description='Detector Response Data Format library',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://baltig.infn.it/sipmat/drdf',  # Optional
    author='Nicolo Tosi',  # Optional
    author_email='nicolo.tosi@bo.infn.it',  # Optional
    packages=find_packages(where='.'),  # Required
    python_requires='>=3.6, <4',
    install_requires=[''],  # Optional
)

