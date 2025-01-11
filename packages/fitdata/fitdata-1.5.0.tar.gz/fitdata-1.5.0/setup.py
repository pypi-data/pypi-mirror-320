from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fitdata",
    version="1.5.0",
    packages=find_packages(),
    description="A Python package for managing fitness-related data and goals.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Monsieur Nobody",
    author_email="monsieurnobody01@gmail.com",
    url="https://gitlab.com/misternobody01/fitdata.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    keywords="fitness health bmi bmr tdee macros python",
    license="MIT",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
    ],
)
