from setuptools import setup, find_packages


def read_requirements():
    with open("requirements.txt", encoding="UTF-16") as f:
        return [line for line in f.read().splitlines() if "@" not in line]

setup(
    name="IFE_Surrogate",
    version="0.1.1",
    description="A brief description of your library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-repo",
    packages=find_packages(),
    install_requires=read_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)