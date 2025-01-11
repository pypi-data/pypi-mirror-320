from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ddddocr-basic",
    version="1.5.6.post2",
    author="WaterLemons2k",
    description="Basic version of ddddocr",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WaterLemons2k/ddddocr-basic",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy', 'onnxruntime', 'Pillow'],
    python_requires='>=3.10',
)
