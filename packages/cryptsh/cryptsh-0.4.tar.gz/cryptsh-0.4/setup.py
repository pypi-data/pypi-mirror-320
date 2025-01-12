from setuptools import setup, find_packages

setup(
    name="cryptsh",  # Choose a unique package name
    version="0.4",
    packages=find_packages(),
    install_requires=[  # Dependencies that your app needs
        "python-binance",
        "tabulate",
        "mysql-connector-python",
        "keyboard",
        "psycopg2",
        
    ],
    entry_points={  # If your script is executable
        "console_scripts": [
            "cryptsh = cryptsh.main:main",  # Adjust the module name and function
        ],
    },
    include_package_data=True,
    package_data={
        'cryptsh': ['intents.json'],  # Include intents.json file in the package
    },
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[  # Categorize your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
