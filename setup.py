from setuptools import setup, find_packages

import witnet_net_api


def install_deps():
    """Reads requirements.txt and preprocess it
    to be feed into setuptools.
    This is the only possible way (we found)
    how requirements.txt can be reused in setup.py
    using dependencies from private github repositories.
    Links must be appendend by `-{StringWithAtLeastOneNumber}`
    or something like that, so e.g. `-9231` works as well as
    `1.1.0`. This is ignored by the setuptools, but has to be there.
    Returns:
         list of packages and dependency links.
    """
    with open('requirements.txt', 'r') as f:
        packages = f.readlines()
        new_pkgs = []
        for resource in packages:
            new_pkgs.append(resource.strip())
        return new_pkgs


def readme():
    with open('README.md', 'r') as f:
        text = f.read()
    return text


setup(
    name='witnet-net-api',
    version=witnet_net_api.__version__,
    packages=find_packages(exclude=("tests",)),
    description='API cli for witnet net dashboard',
    author='harsh',
    long_description=readme(),
    long_description_content_type="text/markdown",
    author_email='harshjniitr@gmail.com',
    license='MIT',
    url='https://github.com/harsh-98/witnet_lib',
    keywords='witnet blockchain lightclient proto',
    install_requires=[
        "witnet_lib", "witpy", "python-socketio", "toml", "jsonschema"
    ],
    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'License :: OSI Approved :: MIT License'],
    entry_points={
        "console_scripts": [
            "witnet=witnet_net_api.cli:main",
        ],
    }
)
