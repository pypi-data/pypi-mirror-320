from setuptools import find_namespace_packages, setup

setup(
    name="upheaval-proto",
    version="0.0.1",
    author="Upheaval Protocol",
    author_email="contact@upheaval.fi",
    description="Protos for Upheaval Chain protocol",
    packages = find_namespace_packages(),
    include_package_data=True,  # Include files specified in MANIFEST.in
    install_requires=[
        "protobuf>=4.23",
        "grpcio-tools>=1.54",
        "grpcio>=1.54"
    ],
    license_files = ("LICENSE"),
    python_requires=">=3.8",
)
