import setuptools

setuptools.setup(
    name='english_python',
    version='0.1',
    author='Hadi-aljad',
    description="""
My Python Library is a collection of utility functions designed to simplify common programming tasks in Python. 
It provides easy-to-use alternatives to built-in Python functions, making your code more readable and intuitive. 
Whether you're working with strings, lists, dictionaries, files, or mathematical operations, this library has you covered.
""",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)