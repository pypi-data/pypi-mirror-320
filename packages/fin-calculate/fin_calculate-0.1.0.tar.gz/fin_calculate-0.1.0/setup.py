from setuptools import setup, find_packages

setup(
    name="fin_calculate",
    version="0.1.0",
    author="Aleksei Zagorskii",
    author_email="zagorskii.aleksei.2004@gmail.com",
    description="For Numerical methods only so yet",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ju1ceL0ver/fin_calculate.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)