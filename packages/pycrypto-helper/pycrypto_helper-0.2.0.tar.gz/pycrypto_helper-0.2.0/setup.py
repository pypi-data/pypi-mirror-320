from setuptools import setup, find_packages

setup(
    name='pycrypto_helper',
    version='0.2.0',
    description='A helper library for cryptographic operations',
    author='Embetrix',
    author_email='info@embetrix.com',
    url='https://github.com/embetrix/pycrypto-helper',
    packages=find_packages(),
    install_requires=[
        'python-pkcs11',
        'pycryptodomex',
        'asn1crypto'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)