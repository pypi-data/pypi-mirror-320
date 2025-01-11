from setuptools import setup, find_packages
from codecs import open
import os


scriptFolder = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptFolder)

with open('README.md', 'r') as readme_file:
    readme_content = readme_file.read()


setup(
    name='pybenjarvis',
    version='1.1.0',
    description='PyBEN jarvis getter',
    long_description=readme_content,
    long_description_content_type='text/markdown',
    url='https://github.com/DarkFlameBEN/pybenjarvis.git',
    author='Ben Moskovitch',
    author_email='"Ben Moskovitch" <darkflameben@gmail.com>',
    classifiers=[
        # "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Development Status :: 6 - Mature",
        # "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        'Topic :: Software Development :: Libraries',
        # 'License :: OSI Approved :: MIT License',
        # 'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=['requests'],
    include_package_data=True,
    packages=find_packages(exclude=['tests']),
    python_requires='>3'
)
