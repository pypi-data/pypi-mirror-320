from setuptools import setup, find_packages

setup(
    name='aiogram-creator',
    version='1.0.5',
    packages=find_packages(),
    package_data={'': ['aiogram_creator/template/**/*']},
    entry_points={
        'console_scripts': [
            'aiogram-creator = aiogram_creator.main:main',
        ],
    },
    author='What-XD',
    description='Template for generating aiogram bots',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/What-XD/aiogram-creator',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)