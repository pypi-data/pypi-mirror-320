from setuptools import setup

description = """Trinkets is a collection of useful tools and helper scripts.

[wip]
"""

setup(
    name='trinkets',
    version='0.2.5',
    author='Mohamed Abdel-Hafiz',
    author_email='mohamed.abdel-hafiz@cuanschutz.edu',
    description='A group of commonly used functions.',
    install_requires=[
        "requests>=2.32.0",
        'keyring>=24',
        "scikit-learn>=1.5.0",
        'scipy>=1',
        'pyyaml>=6',
        'matplotlib>=3.9'
    ],
    packages=['trinkets'],
    package_dir={'': 'src'},
    license='MIT',
    long_description=description,
    python_requires='>=3.9'
)
