from setuptools import setup, find_packages

setup(
    name='ml12',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    author="25/25 in lab",
    author_email="your_email@example.com",
    description="A custom Python package with multiple programs.",
    python_requires='>=3.6',
)
#python setup.py sdist bdist_wheel
#twine upload dist/*