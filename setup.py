from setuptools import setup, find_packages

setup(
    name='recipe_telegram_bot',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'aiogram==2.25.2',
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'start-bot=main:main',
        ],
    },
)
