from setuptools import setup, find_packages

setup(
    name="turbochm",
    version="0.4.0",
    packages=find_packages(),
    install_requires=[
        "pyperclip>=1.8.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
