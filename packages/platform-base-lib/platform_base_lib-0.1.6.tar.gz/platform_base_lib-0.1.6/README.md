# **Platform Base Library**

`platform_base_lib` is a Python library designed as a foundational component for managing project infrastructure using gRPC protocol buffers. This project simplifies and standardizes common tasks such as communication setup, protobuf compilation, and offering shared functionalities for base setup.

## Table of Contents

1. [Features](#features)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
     - [Install From Git](#install-from-git)
     - [Install From PyPI](#install-from-pypi)
3. [Project Commands Cheatsheet](#project-commands-cheatsheet)
   - [Protobuf File Compilation](#protobuf-file-compilation)
   - [Package Building](#package-building)
4. [Codebase Walkthrough](#codebase-walkthrough)
   - [Repository Structure](#1-repository-structure)
   - [Key Components](#2-key-components)
     - [Protobuf Management](#protobuf-management)
     - [Dependencies](#dependencies)
5. [Usage](#usage)
6. [License](#license)

---

## **Features**

- **gRPC Support**: Automatically compile `.proto` files to Python bindings for gRPC services (`*_pb2.py` and `*_pb2_grpc.py`).
- **Declarative Configuration**: Simplifies package setup using `setup.cfg` and supports easy installation and dependency management.
- **Extensible**: Provides functionality to build on top of existing gRPC infrastructure.

---

## **Getting Started**

### **Prerequisites**

Ensure you have the following installed:

- **Python** >= 3.12
- **Pip** >= 20.x.x
- Build tools for Python packaging:
  ```bash
  pip install -r requirements.txt
  ```

If you're working with the gRPC protocol buffers, you’ll also need:

- `grpcio` and `grpcio-tools` for protocol buffer compilation.

---

### **Installation**

#### **Install From Git**

You can install the `platform_base_lib` directly from the source repository:

```bash
pip install git+https://github.com/KJBNAgtechPlatform/PlatformBaseLib.git@main#egg=platform_base_lib

```

#### **Install From PyPI**

To install the library from PyPI (after publishing):

```bash
pip install platform_base_lib
```

---

## **Project Commands Cheatsheet**

### **Protobuf File Compilation**

Run the custom `generate_protos` command to compile `.proto` files into Python bindings:

```bash
python setup.py generate_protos
```

### **Package Building**

To generate source (`.tar.gz`) and wheel (`.whl`) distributions:

```bash
python setup.py sdist bdist_wheel
```

The distribution files will be located in the `dist/` folder.

---

## **Codebase Walkthrough**

### **1. Repository Structure**

```plaintext
platform_base_lib/
├── .env                        # Environment variables configuration
├── .gitignore
├── README.md                   # Project documentation
├── requirements.txt            # Project dependencies
├── main.py                   # Entry Point
├── docker-compose.yml        # Docker services configuration
│
├── base_lib/                 # Main package directory
│   ├── __init__.py
│   │
│   ├── configs/             # Configuration management
│   │   ├── __init__.py
│   │   └── config.py       # Settings and environment configuration
│   │
│   ├── infra/              # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── grpc/          # gRPC related code
│   │   │   ├── __init__.py
│   │   │   ├── proto/     # Protocol buffer definitions (git submodule)
│   │   │   └── clients/   # gRPC client implementations
│   │   │
│   │   └── db/           # Database related code
│   │       ├── __init__.py
│   │       ├── mysql/    # MySQL specific implementations
│   │       └── redis/    # Redis specific implementations
│   │
│   ├── domain/           # Business logic layer
│   │   ├── __init__.py
│   │   ├── entities/     # Business entities
│   │   └── use_cases/    # Business use cases
│   │
│   ├── app/             # Application layer
│   │   ├── __init__.py
│   │   ├── services/    # Service orchestration
│   │   ├── api/        # API definitions
│   │   └── tasks/      # Background tasks
│   │
│   └── interfaces/      # Interface definitions
│       ├── __init__.py
│       ├── interactor/  # Interface implementations
│       └── db_model/    # Database models
│
├── tests/               # Test directory
│   ├── __init__.py
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── conftest.py     # Test configurations
│
├── docs/               # Documentation
│   └── api/           # API documentation
│
└── db-data/           # Database volume mount point (git-ignored)
    ├── mysql/         # MySQL data
    └── test-db-data/  # Test database data
```

### **2. Key Components**

#### **Protobuf Management**

All `.proto` files are stored git submodule under `base_lib/infra/grpc/proto/`. These files define gRPC services and message types.
git repo `https://github.com/KJBNAgtechPlatform/protos`

Example Usage:

```
from platform_base_lib.infra.grpc.proto import auth_pb2, auth_pb2_grpc

class MyAuthService(auth_pb2_grpc.AuthServiceServicer):
    def Login(self, request, context):
        # Process login requests
        return auth_pb2.LoginResponse(success=True)
```

#### **Dependencies**

Listed in `requirements.txt`, and must be installed for the package to work:

```plaintext
grpcio==1.56.2
grpcio-tools==1.56.2
pytest==7.4.2
numpy==1.25.0
pandas==2.1.0
```

For development dependencies, use:

```bash
pip install -e .[dev]
```

---

## **Usage**

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/KJBNAgtechPlatform/PlatformBaseLib.git

   cd PlatformBaseLib
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Compile `.proto` Files:**

   ```bash
   python setup.py generate_protos
   ```

4. **Build and Distribute the Package:**

   ```bash
   python setup.py sdist bdist_wheel
   ```

5. **Use the Package in Another Project:**
   Install the wheel (`.whl`) file or use Git for installation:
   ```bash
   pip install git+https://github.com/KJBNAgtechPlatform/PlatformBaseLib.git@main#egg=platform_base_lib
   ```

---

## **License**

This library is licensed under the MIT License. See `LICENSE` for details.
