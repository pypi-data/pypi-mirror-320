from setuptools import setup, find_packages

setup(
    name="adarsh",  # Choose a unique package name
    version="0.0.2",
    packages=find_packages(),
    install_requires=[  # Dependencies that your app needs
              
    ],
    entry_points={  # If your script is executable
        "console_scripts": [
            "adarsh = adarsh.main:intro",  # Adjust the module name and function
        ],
    },
    include_package_data=True,
    
    
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[  # Categorize your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
