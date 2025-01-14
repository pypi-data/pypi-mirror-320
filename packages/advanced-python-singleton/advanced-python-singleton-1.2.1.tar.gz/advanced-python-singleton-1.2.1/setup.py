from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='advanced-python-singleton',
    version='1.2.1',
    author='jogakdal',
    author_email='jogakdal@gmail.com',
    description='Singleton & TtlSingleton meta-class',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jogakdal/advanced-singleton',
    install_requires=['expiringdict'],
    packages=find_packages(exclude=[]),
    keywords=['jogakdal', 'Singleton', 'TTL', 'metaclass'],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
