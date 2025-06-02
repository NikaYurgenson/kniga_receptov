from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='recipe-telegram-bot',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.10,<3.11',
    entry_points={
        'console_scripts': [
            'recipe-bot=main:main',
        ],
    },
)
