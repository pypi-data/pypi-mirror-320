import v2v_toolkit
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name=v2v_toolkit.__title__,
    version=v2v_toolkit.__version__,
    packages=find_packages(),
    description=v2v_toolkit.__description__,
    long_description="""**Ver2Vision Toolkit** library aims to deliver a unified interface and tools to facilitate the development and execution of *Verbal Data to Vision Synthesis with Latent Diffusion Models* project. 
Provides tools for managing downstream tasks like execution graphs, scheduling, low-level parallelism, and handling dependencies resolution, allowing developers to focus on extending core modules and defining concise configurations. 
Built-in support for fault tolerance, system and processes monitoring, custom configuration and scalable execution, `v2v` library streamlines the process of running experiments in `Ver2Vision` project.
""",
    long_description_content_type="text/markdown",
    author=v2v_toolkit.__author__,
    author_email=v2v_toolkit.__email__,
    url=v2v_toolkit.__url__,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
)
