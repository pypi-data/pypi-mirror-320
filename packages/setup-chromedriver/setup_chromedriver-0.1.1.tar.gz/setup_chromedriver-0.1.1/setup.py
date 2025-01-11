from setuptools import setup, find_packages

setup(
    name="setup-chromedriver",  # Unique name for your library on PyPI
    version="0.1.1",  # Start with 0.1.0, and update for new releases
    description="A Python library to automatically manage and set up ChromeDriver.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Rasikh Ali",
    author_email="rasikh.ali1234@gmail.com",  # Replace with your email
    url="https://github.com/RasikhAli/setup_chromedriver",  # Link to your GitHub repo
    packages=find_packages(),  # Automatically find the package directory
    install_requires=[
        "selenium",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
