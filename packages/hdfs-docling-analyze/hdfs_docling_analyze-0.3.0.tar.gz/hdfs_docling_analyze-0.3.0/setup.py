from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="hdfs_docling_analyze",
    version="0.3.0",
    description="A library for analyzing files from HDFS and saving results to MongoDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vo Nhu Y",
    author_email="vonhuy5112002@gmail.com",
    url="https://github.com/vonhuy1",
    packages=find_packages(),
    package_data={  
        "": ["third_party/*.whl"],  # Bao gồm tất cả các file .whl trong thư mục third_party
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
