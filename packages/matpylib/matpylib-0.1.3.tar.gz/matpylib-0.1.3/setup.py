from setuptools import setup, find_packages

setup(
    name='matpylib',
    version='0.1.3',
    description='darkball',
    author='darkball',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'webdriver-manager',
        'pywin32',
        'keyboard',
    ],
    entry_points={
        'console_scripts': [
            'matpylibrun=matpylib.core:main',
        ],
    },
)
