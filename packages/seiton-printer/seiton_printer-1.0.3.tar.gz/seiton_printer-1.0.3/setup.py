from setuptools import setup

setup(
    name="seiton_printer",
    version="1.0.3",
    packages=["seiton_printer"],
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
