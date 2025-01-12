from setuptools import setup, find_packages

setup(
    name="lumbni-client",
    version="1.0.1",  # Make sure this version is updated
    author="Lumbni",
    author_email="lumbniai@gamil.com",
    description="A Python SDK for interacting with the Lumbni API",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
