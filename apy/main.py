from fastapi import FastAPI, Response
from json import loads
from pathlib import Path
from sqlite3 import connect, Connection
from uvicorn import run

app: FastAPI = FastAPI()
connection: Connection = connect(Path(__file__).parent.joinpath("data/apy.db"))


def main() -> None:
    run(f"{__name__}:app", reload=True)


@app.get("/")
async def root() -> str:
    document: str = Path(__file__).parent.joinpath("ui/index.html").read_text()
    rows: list = await select()
    row: dict
    content: str = ""

    for row in rows:
        content += f"""
                <tr>
                    <td>{row[0]}</td>
                    <form action='http://127.0.0.1:8000/users/update/{row[0]}' method='POST'>
                        <td><input name='first_name' value='{row[1]}'></td>
                        <td><input name='last_name' value='{row[2]}'></td>
                        <td><input name='email' value='{row[3]}'></td>
                        <td class='text-align-center'><input name='update' type='submit' value='☑' onclick='updateUser({row[0]});'></td>
                    </form>
                    <td class='text-align-center'><input name='delete' type='button' value='☒' onclick='deleteUser({row[0]})'></td>
                </tr>"""

    return Response(document.replace("%CONTENT%", content), media_type="text/html")


@app.get("/health")
async def health() -> dict:
    return {"message": "The state of the service is healthy."}


@app.get("/hello")
async def hello() -> dict:
    return {"message": "Hello World !"}


@app.post("/init")
async def init() -> dict:
    await drop()
    await create()
    users: list = loads(Path(__file__).parent.joinpath("data/users/data.json").read_text())
    await insert(users)

    return {"message": "Database initialized."}


@app.post("/calc/{operator}")
async def calc(operator: str, terms: list[float]) -> dict:
    result: float   

    if operator in ["*", "/", "÷"]:
        result = 1

        if operator == "÷":
            operator = "/"

    else:
        result = 0

    term: float

    for term in terms:
        result = eval(f"result {operator} term")

    return {"result": result}


@app.post("/users/drop")
async def drop() -> dict:
    sql: str = Path(__file__).parent.joinpath("data/users/drop.sql").read_text()
    connection.cursor().execute(sql)

    return {"message": "User table dropped."}


@app.post("/users/create")
async def create() -> dict:
    sql: str = Path(__file__).parent.joinpath("data/users/create.sql").read_text()
    connection.cursor().execute(sql)

    return {"message": "User table created."}


@app.get("/users/select")
@app.get("/users/select/{id}")
async def select(id: str = None) -> list:
    sql: str
    rows: list
    
    if id:
        sql = Path(__file__).parent.joinpath("data/users/select.sql").read_text()
        rows = connection.cursor().execute(sql, (id,)).fetchall()

    else:
        sql = Path(__file__).parent.joinpath("data/users/select_all.sql").read_text()
        rows = connection.cursor().execute(sql).fetchall()
    
    return rows


@app.post("/users/insert")
async def insert(users: list[dict]) -> dict:
    sql: str = Path(__file__).parent.joinpath("data/users/insert.sql").read_text()
    user_tuples: list[tuple] = [tuple(user.values()) for user in users]
    connection.cursor().executemany(sql, user_tuples)
    connection.commit()

    return {"message": "User created."}


@app.post("/users/update/{id}")
@app.put("/users/update/{id}")
async def update(id: str, user: dict) -> dict:
    sql: str = Path(__file__).parent.joinpath("data/users/update.sql").read_text()
    user["id"] = id
    user_tuple = tuple(user.values())
    connection.cursor().execute(sql, user_tuple)
    connection.commit()

    return {"message": "User updated."}


@app.delete("/users/delete/{id}")
async def delete(id: str) -> dict:
    sql: str = Path(__file__).parent.joinpath("data/users/delete.sql").read_text()
    connection.cursor().execute(sql, (id,))
    connection.commit()

    return {"message": "User deleted."}
