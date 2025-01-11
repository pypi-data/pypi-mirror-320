from setuptools import setup, find_packages

setup(
    name="mavera",  # changed from mavera-sdk to mavera
    version="0.1.5",
    description="Python SDK for interacting with the Mavera API",
    author="Alex Hassan",
    author_email="your.email@example.com",  # replace with your actual email
    url="https://github.com/LubedB1nary/mavera",  # GitHub URL reflecting your username and repo name
    package_dir={"": "src"},  # packages are under src/
    packages=find_packages(where="src"), 
    install_requires=[
        "httpx>=0.18.0",
        # add any other dependencies your SDK requires
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
