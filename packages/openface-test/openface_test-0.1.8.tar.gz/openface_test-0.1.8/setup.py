from setuptools import setup, find_packages

setup(
    name='openface-test',
    version='0.1.8',
    packages=find_packages(include=['openface', 'openface.*']),
    include_package_data=True,  # Include data files in the package
    package_data={
        'openface': ['**/*'],  # Include all files in the openface directory
    },
)