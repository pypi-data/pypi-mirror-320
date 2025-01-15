from setuptools import setup, find_packages

setup(
    name='matpylib',
    version='0.1.4',
    description='darkball',
    author='darkball',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'webdriver-manager',
        'pywin32',
        'keyboard',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'matpylibrun=matpylib.core:main',
        ],
    },
)
