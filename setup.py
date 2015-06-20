from setuptools import setup

setup(
    name='pbl',
    version='1.0.1',
    description='A Python library for building playlists',
    author="@plamere",
    author_email="paul@spotify.com",
    url='http://pbl.readthedocs.org/',
    install_requires=['requests>=2.5', 'pyen>=2.3', 'spotipy>=2.0'],
    license='LICENSE.txt',
    packages=['pbl'])
