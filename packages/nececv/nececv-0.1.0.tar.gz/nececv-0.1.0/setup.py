from setuptools import setup, find_packages

setup(
    name="nececv",
    version="0.1.0",
    description="Advanced edge detection and object recognition using VGG16 and OpenCV.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Singhai Kshitij Jain",
    author_email="singhaikshitij143@gmail.com",
    url="https://github.com/singhaikshitijjain/nececv",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "Pillow",
        "tensorflow",
        "opencv-python",
        "matplotlib",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
