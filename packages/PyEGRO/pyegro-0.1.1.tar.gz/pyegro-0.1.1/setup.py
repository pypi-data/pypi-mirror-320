from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PyEGRO",
    version="0.1.1",
    author="Thanasak Wanglomklang",
    author_email="thanasak.wanglomklang@ec-lyon.fr",
    description="A Python library for efficient global robust optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/twanglom/PyEGRO",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "torch",
        "gpytorch",
        "scikit-learn",
        "pymoo",
        "rich",
        "pyDOE",
        "SALib",
        "Pillow",
        "joblib",
        "optuna",
    ],
)