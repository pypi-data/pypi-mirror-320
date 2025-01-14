from setuptools import setup, find_packages

setup(
    name='matpylib',
    version='0.1.0',
    description='db',
    author='darkball',
    packages=find_packages(),
    install_requires=[
        'pywin32',   # для работы с Win32 API
        'keyboard',  # для регистрации горячих клавиш
    ],
    entry_points={
        'console_scripts': [
            'runhidden=matpylib.core:main',  # консольная команда для запуска приложения
        ],
    },
)
