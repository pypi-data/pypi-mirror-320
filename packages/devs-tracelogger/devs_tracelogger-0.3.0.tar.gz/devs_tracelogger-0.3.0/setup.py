from setuptools import setup, find_packages

setup(
    name="devs_tracelogger",
    version="0.3.0",
    author="Gelson Júnior",
    author_email="gelson.junior@grupobachega.com.br",
    description="Uma biblioteca para registrar logs e enviar notificações de erro para o Discord e MongoDB",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/originalprecatorios/tracelogger",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pymongo"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
