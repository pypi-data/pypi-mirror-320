from setuptools import setup

setup(
    name="lilliepy-protect",
    packages=["lilliepy_protect"],
    version="1.0",
    author="sarthak ghoshal",
    author_email="sarthak22.ghoshal@gmail.com",
    description="A protection decorator to protect components",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/websitedeb/lilliept-protect",
    install_requires= [
        "reactpy",
        "reactpy_router"
    ],
    keywords=["reactpy", 
              "lilliepy", 
              "lilliepy_protect"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
