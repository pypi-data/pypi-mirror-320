from setuptools import setup, find_packages

# Function to parse the requirements file
def parse_requirements(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="inbox4us_pos_printer",                # Package name
    version="0.1.0",                  # Version
    packages=find_packages(),         # Automatically find subpackages
    install_requires=parse_requirements("requirements.txt"),  # Dependencies
    author="Daniel",
    description="A brief description of your package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/repository",  # GitHub repository link
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
