from setuptools import setup, find_packages


setup(
    name='pratix_nelog',
    version='0.2.2',
    author="Pratik",
    author_email="your_email@example.com",
    description="A library to analyze network logs in multiple formats and consolidate them into JSON.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pratiklahudkar/pratix-nelog",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

