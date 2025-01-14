from setuptools import setup, find_packages

setup(
    name="gyros",  # package name
    version="0.1.0",  # version
    packages=find_packages(),  # Automatically finds package folders
    install_requires=[  # future dependencies
        # 'dependency_name>=version',
    ],
    description="A distributed computing framework inspired by ROS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ido Rachbuch",
    author_email="idor777@gmail.com",
    url="https://github.com/ido-rachbuch/gyros",  # GitHub repo URL
    license="BSD 3-Clause License",
    classifiers=[  # Add PyPI classifiers
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
