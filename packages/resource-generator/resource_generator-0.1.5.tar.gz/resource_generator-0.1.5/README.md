# Resource Generator For FastApi
___
**Source Code:** [https://github.com/RatanaKH/resource_generator](https://github.com/RatanaKH/resource_generator)

## Overview
A `generate` command for a FastAPI project simplifies the creation of common components like models, controllers, services, and schemas. It acts as a code scaffolding tool, ensuring consistent structure, reducing boilerplate, and accelerating development.

### Key Reasons for Creating a generate Command
1. Consistency Across the Codebase:
Enforcing a consistent naming convention and folder structure.
Preventing errors caused by manual file creation and misplaced code.
Ensuring that all components follow best practices and are aligned with project standards.

1. Improved Developer Productivity:
Automating repetitive tasks like creating models, schemas, and services.
Reducing time spent writing boilerplate code for new components.
Allowing developers to focus on business logic instead of setup tasks.

1. Scalability for Large Teams:
Standardizing the creation process for teams to minimize onboarding effort.
Reducing human errors and misunderstandings regarding file and module organization.
Making collaboration smoother by enforcing project guidelines automatically.

1. Maintainability:
Encouraging modular and predictable code organization.
Generating components with pre-defined templates ensures maintainable and testable code.
Easy refactoring and debugging, as all components are structured consistently.


## Installation

To install this package, use pip:

```bash
  pip install resource-generator
```

To install this package, use poetry:
````shell
  poetry add resource-generator
````

## How to use command

````shell
  ratana-pls make-[OPTION] name [FILE_NAME]
````

### Example:
```shell
  ratana-pls make-model name Users
  
  # Generate model and Users Controller
  ratana-pls make-model name Users --controller 
  
  # Generate model and Users Service
  ratana-pls make-model name Users --service
  
  # Generate model and Users Schema
  ratana-pls make-model name Users --schema 
  
  # Generate model and Users Repository
  ratana-pls make-model name Users --repository 
```
```shell
  ratana-pls make-controller name Users
```
```shell
  ratana-pls make-repository name Users
```
```shell
  ratana-pls make-schema name Users
```
```shell
  ratana-pls make-service name Users
```



#### Sample project structure
```
Project-Name
├── app
│   ├── controllers
│   ├── services
│   ├── models
│   ├── schemas
│   ├── repository
│   ├── router.py
│   ├── main.py
├── poetry.lock
├── package.json
├── pyproject.toml
└── .gitignore
```

___

This package is built on the [typer](https://github.com/fastapi/typer) library.
