from setuptools import setup, find_packages

setup(
    name='CodexGen',
    version='1.0.0',
    description='Library to convert digital data into DNA sequences and vice versa',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Arif Maulana Azis',
    author_email='titandigitalsoft@gmail.com',
    url='https://github.com/Arifmaulanaazis/CodexGen',
    packages=find_packages(where='codexgen'),
    package_dir={'': 'codexgen'},
    include_package_data=True,
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    test_suite='nose.collector',
    tests_require=['nose'],
    license='Apache 2.0',
)