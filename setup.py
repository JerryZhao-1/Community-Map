from setuptools import setup, find_packages

with open("image_detection_package/requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="landmark_recognition",
    version="0.1.0",
    author="JerryZhao-1",
    author_email="jerry.zhao800477-biph@basischina.com",
    description="A package for landmark recognition using a local model and Baidu API.",
    long_description=open("image_detection_package/README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JerryZhao-1/Community-Map",
    packages=['image_detection_package'],
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        'image_detection_package': ['*.pt'],
    },
)
