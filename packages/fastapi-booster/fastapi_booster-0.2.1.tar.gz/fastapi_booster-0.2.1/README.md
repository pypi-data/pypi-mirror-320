# FastAPI Booster

FastAPI Booster is a library that provides a set of tools and utilities to enhance the development experience with FastAPI. It aims to streamline common tasks, provide additional functionality, and make the development process more efficient.

This work is licensed under CC BY-NC-ND 4.0. To view a copy of this license, visit <https://creativecommons.org/licenses/by-nc-nd/4.0/>

## Features

- **Authenticator**: Built-in support for JWT and HTTP Basic authentication.
- **Module**: Built-in support for Module, aka microservice with independent database and router.
- **Lifespan Manager**: Easy to manage the lifespan of the application, with `startup_function` and `shutdown_function` decorator.
- **Certificate Manager**: Utility to manage certificates and keys.
- **Akatosh**: Built-in support for Akatosh, a powerful tool for managing server side real time tasks.

## Example
```python
import uvicorn
from fastapi import Depends, FastAPI
from fastapi_booster.LifeSpanManager import lifespan
from fastapi_booster.Authenticator import JWT
from fastapi_booster.Module import Module
from sqlalchemy.orm import MappedColumn, mapped_column

# Create the FastAPI app with the lifespan manager
app = FastAPI(lifespan=lifespan)

# Create the JWT authenticator
jwt = JWT.JWT()

# Include the JWT router in the FastAPI app
app.include_router(jwt.router)

# Create the root route with the JWT authenticator
@app.get("/", dependencies=[Depends(jwt)])
async def root():
    return {"message": "Hello World"}

# Create the my_module
my_module = Module("my_module", "This is my module")

# Create the my_table
class my_table(my_module.model):
    __tablename__ = "my_table"
    id: MappedColumn[int] = mapped_column(primary_key=True)
    name: MappedColumn[str] = mapped_column()
    age: MappedColumn[int] = mapped_column()
    gender: MappedColumn[str] = mapped_column()

# Create the my_module root route
@my_module.router.get("/my_module")
async def my_module_root():
    return {"message": "Hello World from my_module"}

# Include the my_module router in the FastAPI app
app.include_router(my_module.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

```