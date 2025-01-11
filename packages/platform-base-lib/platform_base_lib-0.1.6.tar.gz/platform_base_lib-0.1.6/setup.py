import os
import subprocess
from setuptools import setup, find_packages, Command

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()


# # Custom command for protobuf generation
# class GenerateProtos(Command):
#     description = "Generate Python code from .proto files"
#     user_options = []
#
#     def initialize_options(self):
#         pass
#
#     def finalize_options(self):
#         pass
#
#     def run(self):
#         proto_dir = os.path.join("base_lib", "infra", "grpc", "proto")
#         if not os.path.exists(proto_dir):
#             print(f"Proto directory not found: {proto_dir}")
#             return
#         for proto_file in os.listdir(proto_dir):
#             if proto_file.endswith(".proto"):
#                 print(f"Compiling {proto_file}...")
#                 subprocess.check_call([
#                     "python", "-m", "grpc_tools.protoc",
#                     f"--proto_path=.",
#                     f"--python_out=.",
#                     f"--grpc_python_out=.",
#                     f"--pyi_out=.",
#                     os.path.join(proto_dir, proto_file)
#                 ])


setup(
    name="platform_base_lib",
    version="0.1.6",
    author="Utkarsh Raj",
    author_email="utkarsh.raj@kjbnlabs.in",
    description="Common library for Base Setup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KJBNAgtechPlatform/PlatformBaseLib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=required,
    # cmdclass={
    #     'generate_protos': GenerateProtos,  # Register protobuf command
    # },
)
