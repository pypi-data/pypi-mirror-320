from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="AIGuard",
    version="0.1.0",
    author="SyntaxSama",
    author_email="syntaxsama@gmail.com",
    description="A system to protect AI from misuse and harmful inputs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SyntaxSama/AIGuard",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "AIGuard": ["manipulation_rules.txt", "settings.yml"],
    },
    install_requires=[
        "ollama"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)