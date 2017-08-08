from setuptools import setup, find_packages

setup(
    name='aethelometer_collector',
    version='0.1',
    description='Data collector for the aethelometer device',
    url='https://github.com/pico-collectors/aethelometer_collector.git',
    license='MIT',
    author='David Fialho',
    author_email='fialho.david@protonmail.com',

    packages=find_packages(),

    install_requires=[],

    extras_require={
        'test': ['pytest', 'hypothesis'],
    },
)
