from setuptools import setup, find_packages

setup(
    name="py-graph-imputation-MLO",
    version="0.1.0",
    description="",
    author="Regev Yehezkel Imra",
    author_email="regevel2006@gmail.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "py-graph-imputation",
        "cython==0.29.32",
        "numpy>=1.20.2",
        "pandas",
        "tqdm"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)