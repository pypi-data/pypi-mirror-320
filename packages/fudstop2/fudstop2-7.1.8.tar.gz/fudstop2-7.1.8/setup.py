from setuptools import setup, find_packages

# Read requirements.txt and remove any comments
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements = [r.strip() for r in requirements if not r.startswith('#')]

setup(
    name='fudstop2',
    version='7.1.8',
    packages=find_packages(),
    install_requires=requirements,
    license="MIT",  # Specify a valid license here
)