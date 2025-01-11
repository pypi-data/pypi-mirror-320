from setuptools import setup, find_packages

setup(
    name="dictionary-app",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.9",
    description="A simple desktop application for managing a personal dictionary of terms and definitions.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Keith Walsh",
    author_email="keithwalsh@gmail.com",
    url="https://github.com/keithwalsh/dictionary-app",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
    ],
    entry_points={
        'console_scripts': [
            'dictionary-app=dictionary_app.main:main',
        ],
    },
)
