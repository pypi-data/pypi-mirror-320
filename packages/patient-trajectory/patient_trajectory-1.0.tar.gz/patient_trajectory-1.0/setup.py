import os
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="patient_trajectory",
    version="1.0",
    author="Dipendra Pant",
    author_email="dipendrapant778@gmail.com",
    description="A package designed to visualize patient trajectories for multiple patients, featuring Gantt-style plots to represent patient episodes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dipendrapant/patient_trajectory",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        # "scipy" if you want to require advanced curves
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
