from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='DrawPrint',
    version='0.2.0',
    description='DrawPrint',
    author='huang yi yi',
    author_email='363766687@qq.com',
    packages=find_packages(),
    py_modules=['DrawPrint'],
    python_requires='>=3.6',
    install_requires=[
        "pyfiglet>=0.8.post1",
        "pygame>=2.6.0.post1",
        "gameturtle>=0.280.post1",
        "sprites>=10.3.0.post1",
        "pyecharts>=2.0.6.post1",
        "opencv-python>=4.10.0.83.post1",
        "requests>=2.32.2.post1",
        "pywin32>=307.post1",
        "pillow>=10.3.0.post1",
    ]
)