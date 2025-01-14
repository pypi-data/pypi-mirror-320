from setuptools import setup, find_packages

setup(
    name="LinearRegressionMeriem",
    version="0.1.1",
    description="A simple linear regression model",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Meriem Terki",
    author_email="mrmterki@gmail.com",
    url="https://github.com/yourusername/LinearRegression",
    packages=find_packages(),
    install_requires=["numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)