from setuptools import setup, find_packages

setup(
    name="nodepulse",
    version="1.1.4",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "schedule>=1.1.0",
        "python-dotenv>=0.19.0"
    ],
    author="NodePulse",
    author_email="charles@sentnl.io",
    description="A Python library to maintain and utilize a list of healthy nodes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sentnl/nodepulse-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    package_data={"": ["LICENSE"]},
    include_package_data=True,
) 