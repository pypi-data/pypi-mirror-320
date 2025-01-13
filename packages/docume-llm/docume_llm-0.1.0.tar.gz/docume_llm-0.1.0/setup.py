from setuptools import setup, find_packages

setup(
    name="docume_llm",  # Your package name
    version="0.1.0",  # Initial version
    description="A Python package for document processing with LLMs",
    long_description=open("README.md").read(),  # Use your README.md as the long description
    long_description_content_type="text/markdown",  # Markdown support for PyPI
    author="Bipin Paudel",  # Your name
    author_email="paudelbipin.bp@gmail.com",  # Your email
    url="https://github.com/BipinPaudel/documee_llm",  # Link to your project repository
    packages=find_packages(),  # Automatically find all packages in your directory
    install_requires=open("requirements.txt").read().splitlines(),  # Dependencies from requirements.txt
    entry_points={
        "console_scripts": [
            "docume_llm=docume_llm.main:generate_documentation",  # Exposes a CLI command 'docume_llm'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Minimum Python version
)