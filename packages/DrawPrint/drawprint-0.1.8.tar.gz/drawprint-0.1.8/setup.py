from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='DrawPrint',
    version='0.1.8',
    description='DrawPrint',
    author='huang yi yi',
    author_email='363766687@qq.com',
    packages=find_packages(),
    py_modules=['DrawPrint'],
    python_requires='>=3.6',
    install_requires=[
        "pyfiglet>=0.8.post1",
        "pygame>=2.6.0.post1",
        "gameturtle>=0.281.post1",
        "sprites>=10.4.0.post1",
        "pyecharts>=2.0.7.post1",
    ]
)