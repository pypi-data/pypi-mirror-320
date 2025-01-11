from setuptools import setup, find_packages

setup(
    name="lillie-start",  
    version="0.1.2",  #update
    packages=find_packages(),  
    py_modules=["start"],  
    install_requires=[
        "typer[all]",  
        "colorama",    
    ],
    entry_points={
        "console_scripts": [
            "start-lillie=start:start",  
        ],
    },
    author="Sarthak Ghoshal",
    description="A script to run lillie.config.py with a terminal command.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
