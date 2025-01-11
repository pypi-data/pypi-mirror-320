# fastapi_easy_crud

`fastapi_easy_crud` is a lightweight and reusable library designed to simplify the implementation of CRUD operations in FastAPI applications. It provides an `AbstractCRUD` class and `BaseFilter` to streamline common database operations and query filtering for models using SQLModel.

---

## Features

- **AbstractCRUD Class**:
  - Create, retrieve, update, and delete operations.
  - Error handling for `NotFoundError` and `DatabaseError`.
  - Timestamps (`created_at`, `modified_at`) for tracking changes.

- **BaseFilter Class**:
  - Apply dynamic filtering to SQLModel queries.
  - Sorting and pagination support for query results.

- **Generic and Flexible**:
  - Easily adaptable to any SQLModel-based FastAPI application.
  - Designed with clean separation of concerns.

---

## Installation

Install the package using pip:

```bash
pip install fastapi_easy_crud
```

---

## Usage

### Prerequisites

Ensure you have the following dependencies installed in your FastAPI project:

- `fastapi`
- `sqlmodel`

---

### 1. Define a Model

Create an SQLModel class for your entity. For example:

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
```

### 2. Initialize the AbstractCRUD

Use the `AbstractCRUD` class to perform CRUD operations for your model:

```python
from fastapi_easy_crud.base_crud import AbstractCRUD
from sqlmodel import Session, create_engine

# Set up the database engine and session
engine = create_engine("sqlite:///database.db")
with Session(engine) as session:
    user_crud = AbstractCRUD(model=User, db_session=session)

    # Create a new user
    new_user = User(name="John Doe", email="john@example.com")
    created_user = user_crud.create(new_user)

    # Retrieve a user by ID
    retrieved_user = user_crud.get(created_user.id)

    # Update a user
    updated_data = User(name="John Updated")
    updated_user = user_crud.update(created_user.id, updated_data)

    # Delete a user
    user_crud.delete(created_user.id)
```

### 3. Using Filters

The `BaseFilter` class enables dynamic filtering, sorting, and pagination:

```python
from fastapi_easy_crud.base_filter import BaseFilter

class UserFilter(BaseFilter):
    name: Optional[str] = None
    email: Optional[str] = None

# Example usage
filter = UserFilter(name="John")
filtered_users = user_crud.get_all(filter_field=filter, sort_field="name", ascending=True, skip=0, limit=10)
```

---

## Exception Handling

The package includes custom exceptions for better error handling:

- `NotFoundError`: Raised when a record is not found.
- `DatabaseError`: Raised for database-related errors.

Example:

```python
from fastapi_easy_crud.exceptions import NotFoundError, DatabaseError

try:
    user = user_crud.get(9999)  # Non-existent ID
except NotFoundError as e:
    print(e)
except DatabaseError as e:
    print(e)
```

---

## Contribution

Contributions are welcome! Feel free to fork the repository and submit pull requests.

---

## License

`fastapi_easy_crud` is licensed under the MIT License. See the `LICENSE` file for details.

---

## Author

This package was developed to simplify common CRUD patterns in FastAPI applications. For inquiries, please contact the maintainer.

