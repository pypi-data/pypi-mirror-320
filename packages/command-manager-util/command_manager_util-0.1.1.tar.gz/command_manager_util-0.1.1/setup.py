from setuptools import setup


def read_file():
    with open("README.md", "r", encoding='utf-8') as f:
        content = f.read()
    return content


setup(
    name="command-manager-util",
    version="0.1.1",
    description="This manages all the usesful commands at one place",
    long_description=read_file(),
    long_description_content_type="text/markdown",
    author="Sahaj Pratap Singh",
    url="https://github.com/Sahaj001/Script-Manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires='>=3.6',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'scm=main:start',  # Example command
        ],
    },
    license="Apache 2.0",                    # Specify Apache 2.0 License
)
