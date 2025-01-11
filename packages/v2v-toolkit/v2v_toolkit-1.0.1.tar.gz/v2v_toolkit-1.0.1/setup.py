from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="v2v_toolkit",
    version="1.0.1",
    packages=find_packages(),
    description="Ver2Vision-Toolkit: Unified interface for streamlining 'Verbal Data to Vision Synthesis with Latent Diffusion Models' project. Provides tools for managing low-level downstream tasks.",
    long_description="""**Ver2Vision Toolkit** library aims to deliver a unified interface and tools to facilitate the development and execution of *Verbal Data to Vision Synthesis with Latent Diffusion Models* project. 
Provides tools for managing downstream tasks like execution graphs, scheduling, low-level parallelism, and handling dependencies resolution, allowing developers to focus on extending core modules and defining concise configurations. 
Built-in support for fault tolerance, system and processes monitoring, custom configuration and scalable execution, `v2v` library streamlines the process of running experiments in `Ver2Vision` project.
""",
    long_description_content_type="text/markdown",
    author="Lukasz Michalski, Szymon Lopuszynski, Wojciech Rymer",
    author_email="lukasz.michalski222@gmail.com",
    url="https://github.com/lukaszmichalskii/ver2vision-toolkit",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
)
