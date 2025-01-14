from setuptools import setup, find_packages

setup(
    name="pytc111",
    version="3.1.0",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    author="someone111",
    author_email="tc@tc111xyz.com",
    description="tc local package",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tiacui/testrepo111",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
