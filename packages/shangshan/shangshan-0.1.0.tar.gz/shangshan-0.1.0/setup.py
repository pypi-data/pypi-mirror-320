from setuptools import setup, find_packages

setup(
    name="shangshan",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python SDK for downloading and processing data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/shangshan",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        # 添加其他依赖
    ],
) 