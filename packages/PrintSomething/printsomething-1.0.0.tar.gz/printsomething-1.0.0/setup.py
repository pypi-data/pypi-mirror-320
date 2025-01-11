from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='PrintSomething',
    version='1.0.0',
    description='PrintSomething',
    author='huang yi yi',
    author_email='363766687@qq.com',
    packages=find_packages(),
    py_modules=['PrintSomething'],
    python_requires='>=3.6',
)