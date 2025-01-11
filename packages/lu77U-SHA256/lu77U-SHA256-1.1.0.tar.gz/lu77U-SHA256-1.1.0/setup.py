from setuptools import setup, find_packages

setup(
    name="lu77U-SHA256",
    version="1.1.0",
    author="Sam MG Harish",
    author_email="sammgharish@gmail.com",
    description="An Fully Manual SHA-256 Hasher",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=["click"],
    entry_points={
        "console_scripts": [
            "lu77U-SHA256 = lu77U_SHA256.Main:main"
        ]
    }
)