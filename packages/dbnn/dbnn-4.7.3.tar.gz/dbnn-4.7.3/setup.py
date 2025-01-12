from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dbnn",
    version="4.7.3",
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
        install_requires=[
        'torch>=1.8.0',
        'numpy>=1.19.2',
        'pandas>=1.2.0',
        'scikit-learn>=0.24.0',
        'matplotlib>=3.3.0',
        'seaborn>=0.11.0',
        'pynput>=1.7.0',
    ],
)
