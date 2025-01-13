from setuptools import setup, find_packages

setup(
    name="seiton_printer",
    version="1.0.1",
    packages=find_packages(where="seiton_printer"),
    install_requires=[
        'Pillow'
    ],
    author="Mauro",
    author_email="seiton@eklabs.dev",
    description="Set de metodos para controlar la impresora Seiton",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ernes128/seiton-driver-python",
    python_requires=">=3.6",
)
