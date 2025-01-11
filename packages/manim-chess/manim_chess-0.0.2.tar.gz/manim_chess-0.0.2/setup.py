from setuptools import find_packages, setup

with open("manim_chess/README.md", "r") as f:
    long_description = f.read()

setup(
    name="manim_chess",
    version='0.0.2',
    descriptiopn='A plugin for Manim CE that allows the user to generate a chess board and other chess related functions.',
    package_dir={"": "manim_chess"},
    packages=find_packages(where="manim_chess"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swoyer2/manim_chess",
    author="Swoyer2",
    author_email="swoyer.logan@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License"
    ],
    extras_require={
        "dev": ["twine>=4.0.2"]
    },
)