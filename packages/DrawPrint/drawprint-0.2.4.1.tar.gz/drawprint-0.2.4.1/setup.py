from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='DrawPrint',
    version='0.2.4.1',
    description='DrawPrint',
    author='huang yi yi',
    author_email='363766687@qq.com',
    long_description=long_description,
    packages=find_packages(),
    py_modules=['DrawPrint'],
    python_requires='>=3.6',
    install_requires=[
        "pyfiglet>=0.8.post1",
        "pygame>=2.6.0.post1",
        "pyecharts>=2.0.6.post1",
        "requests>=2.32.2.post1",
        "pypiwin32>=219.post1",
        "cutecharts>=1.1.9",
        "pywebio>=1.8.2",
    ]
)