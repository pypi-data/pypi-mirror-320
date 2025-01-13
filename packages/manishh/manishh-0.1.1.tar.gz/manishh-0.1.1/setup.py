# setup.py

from setuptools import setup, find_packages

setup(
    name="manishh",
    version="0.1.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'manish=manish.cli:main',
            'manish-github=manish.cli:github',  # New command
        ],
    },
    description="A simple greeting package",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/manish",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
