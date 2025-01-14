from setuptools import setup, find_packages

setup(
    name="SimpleFacturaSDK",
    version="1.1.9",
    description="SDK para la integración con los servicios de SimpleFactura",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Carlos Perea",
    author_email="pereacarlos685@gmail.com",
    url="https://github.com/pereacarlos/SimpleFacturaSDK-python",
    packages=find_packages(where="."),
    install_requires=[
        "aiohttp",
        "requests-toolbelt",
        "pydantic",
        "httpx",
        "requests",
        "python-dotenv",
        "aiofiles"
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-asyncio",
            "requests-mock"
        ]
    },
    include_package_data=True,
    package_data={
        "SimpleFacturaSDK": ["log.png"],
    },
    keywords=[
        "dte",
        "factura",
        "boleta",
        "impuestos internos",
        "factura electrónica",
        "boleta electrónica",
        "documento",
        "iva",
        "SII",
        "documento tributario electrónico"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

)