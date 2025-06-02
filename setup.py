from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='recipe_bot',  # Changed to match the import name
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.10,<3.11',
    entry_points={
        'console_scripts': [
            'recipe_bot=recipe_bot.cli:main',
        ],
    },
)
