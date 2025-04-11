from setuptools import setup, find_packages

setup(
    name="langpipe", 
    version="0.0.1",
    author="zhouzhi",
    author_email="zhouzhi9@foxmail.com",
    description="a simple lightweight large language model pipeline framework.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sherlockchou86/VideoPipe",
    packages=find_packages(),
    install_requires=[
        "ollama"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
