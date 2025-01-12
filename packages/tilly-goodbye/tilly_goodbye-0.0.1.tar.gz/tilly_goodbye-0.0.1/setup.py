import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tilly-goodbye",
    version="0.0.1",
    author="Ronald Luitwieler",
    author_email="ronald.luitwieler@gmail.com",
    description="Example plugin for tilly.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tilly-pub/tilly-goodbye",
    packages=setuptools.find_packages(),
    py_modules=["tilly_goodbye"],
    install_requires=[
        "tilly"
    ],
    entry_points={
        "tilly": ["goodbye = tilly_goodbye"],
    },
    python_requires=">=3.9",
)