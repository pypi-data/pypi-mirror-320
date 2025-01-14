from setuptools import setup, find_packages

setup(
    name="lu77U-SHA256",
    version="1.1.3",
    author="Sam MG Harish",
    home_page="https://github.com/sam-mg/Python-SHA-256-Implementation",
    license="Apache Software License 2.0",
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
