from setuptools import setup, find_packages

setup(
    name="suicide_text_predictor",
    version="0.2.3",
    author="Ngoc Duy Bui",
    author_email="buiduyngoc1@gmail.com",
    description="A package to predict if a text is a suicide post or not.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ng0cduy/applied-AI",
    packages=find_packages(),
    install_requires=[
        "torch==2.0.1",
        "torchtext==0.15.2"
    ],
    include_package_data=True,
    package_data={
        "suicide_text_predictor": ["text_prediction.pt", "vocab.pth"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
