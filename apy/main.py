from apy.data.db import *
from fastapi import FastAPI
from pathlib import Path
from sqlite3 import connect, Connection

app = FastAPI()
connection: Connection = connect(Path(__file__).parent.joinpath("data/apy.db"))


@app.get("/")
async def root() -> dict:
    return {"message": "The state of the service is healthy."}


@app.get("/hello")
async def hello() -> dict:
    return {"message": "Hello World !"}


@app.get("/init")
async def init() -> dict:
    response: str = init_users(connection)

    return response


@app.get("/users/select")
async def select() -> list: 
    rows: list = select_users(connection)
    
    return rows


@app.post("/users/insert")
async def insert(entities: list) -> dict:
    users: list[tuple] = [(user["first_name"], user["last_name"], user["email"]) for user in entities]
    insert_users(connection, users)

    return {"message": "User inserted."}


@app.post("/users/update")
async def update(entities: list) -> dict:
    users: list[tuple] = [(user["first_name"], user["last_name"], user["email"], user["id"]) for user in entities]
    update_users(connection, users)

    return {"message": "User updated."}


@app.get("/users/delete/{id}")
async def delete(id: str) -> dict:
    delete_users(connection, id)

    return {"message": "User deleted."}
