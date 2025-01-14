from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='clicommon',
    version='0.2.1',
    description='Python Common Client Library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/franksplace/clicommon',
    author='Frank Stutz',
    author_email='frank@franksplae.net',
    license='Apache-2.0 license',
    packages=['clicommon'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Logging',
    ],
)

