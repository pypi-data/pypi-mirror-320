from setuptools import setup
from codecs import open as codecs_open
from os import path

here = path.abspath(path.dirname(__file__))

with codecs_open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='py3sshpubkeys',
    version='3.4.0',
    description='SSH public key parser',
    long_description=long_description,
    url='https://github.com/ojarva/python-sshpubkeys',
    author='Olli Jarva',
    author_email='olli@jarva.fi',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords='ssh pubkey public key openssh ssh-rsa ssh-dss ssh-ed25519',
    packages=["sshpubkeys"],
    test_suite="tests",
    python_requires='>=3',
    install_requires=['cryptography==43.0.0'],
    setup_requires=['setuptools', 'pytest-runner'],
    tests_require=['pytest'],
    extras_require={
        'dev': ['twine', 'wheel', 'yapf'],
    },
)
