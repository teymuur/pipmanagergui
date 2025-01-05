from setuptools import setup, find_packages

setup(
    name="pipmanagergui",
    version="0.1.1",
    description="A GUI for managing Python packages",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Teymur Babayev",
    author_email="teymur_babayev08@yahoo.com",
    url="https://github.com/teymuur/pipmanagergui",
    license="MIT",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "pipmanager = pipmanager.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)