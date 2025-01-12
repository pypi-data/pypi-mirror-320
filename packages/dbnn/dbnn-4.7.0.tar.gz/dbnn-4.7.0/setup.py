from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dbnn",
    version="4.7.0",
    author="Ninan Sajeeth Philip",
    author_email="nsp@airis4d.com",
    description="Difference Boosting Neural Network Implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sajeethphilip/dbnn",
    packages=find_packages(),
    scripts=['bin/dbnn'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
)
