from setuptools import setup, find_packages

setup(
    name="fckafde-shortener",  # The name of your package
    version="0.1.0",  # Initial version
    author="MeBeBruno",
    author_email="",
    description="A Python library for using the fckaf.de URL shortener.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",  # You can leave this empty or provide a placeholder
    package_dir={"": "src"},  # Your code resides in the 'src' directory
    packages=find_packages(where="src"),  # Automatically find packages in 'src'
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Use an appropriate license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
    install_requires=[
        "requests",  # Required dependencies
        "beautifulsoup4",
    ],
)
