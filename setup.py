import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graces",
    version="0.0.1",
    author="GanjinZero",
    author_email="yuanz17@mails.tsinghua.edu.cn",
    description="Graph Cut Chinese Segment Tool",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/GanjinZero/graces",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
