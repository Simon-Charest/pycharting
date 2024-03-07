from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from json import load, loads
from pathlib import Path
from sqlite3 import connect, Connection
from typing import Any
from uvicorn import run

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory=Path(__file__).parent.joinpath("ui/static")), name="static")
config: dict = load(open(Path(__file__).parent.joinpath("config.json")))
connection: Connection = connect(Path(__file__).parent.joinpath("data/apy.db"))


def main() -> None:
    run(f"{__name__}:app", host=config["host"], port=config["port"], reload=True)


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
                    <td><input id='firstName[{row[0]}]' value='{row[1]}'></td>
                    <td><input id='lastName[{row[0]}]' value='{row[2]}'></td>
                    <td><input id='email[{row[0]}]' value='{row[3]}'></td>
                    <td class='text-align-center'><input name='update' type='button' value='☑' onclick='updateUser({row[0]}, "{config["host"]}", {config["port"]});'></td>
                    <td class='text-align-center'><input name='delete' type='button' value='☒' onclick='deleteUser({row[0]}, "{config["host"]}", {config["port"]});'></td>
                </tr>"""
        
    content += f"""
                <tr>
                    <td></td>
                    <td><input id='firstName' value=''></td>
                    <td><input id='lastName' value=''></td>
                    <td><input id='email' value=''></td>
                    <td class='text-align-center' colspan="2"><input name='insert' type='button' value='⨁' onclick='insertUser("{config["host"]}", {config["port"]});'></td>
                </tr>"""

    return Response(document.replace("%CONTENT%", content), media_type="text/html")


@app.get("/health")
async def health() -> dict:
    return {"message": "The state of the service is healthy."}


@app.get("/hello")
async def hello() -> dict:
    return {"message": "Hello World !"}


@app.get("/init")
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


@app.post("/mortgage")
async def mortgage(request: dict) -> dict[str, Any]:
    """
    Mortgage calculation formula.

    Parameters:
        loan (float): Amount of the loan.
        rate (float): Annual interest rate.
        duration (int): Duration in years.
    """

    # Declaration with order of keys
    result: dict[str, Any] = {
        "request": {},
        "response": {
            "monthly": {
                "capital": None,
                "interest": None,
                "payment": None
            },
            "total": {
                "interest": None,
                "payment": None
            }, "rate": {
                "interest": None,
                "payment": None
            }
        }
    }
    result["request"] = request
    result["response"]["monthly"]["payment"] = round((result["request"]["loan"] * result["request"]["rate"] / 12) / (1 - (1 + result["request"]["rate"] / 12) ** (-12 * request["duration"])), 2)  # Mortgage calculation formula.
    result["response"]["total"]["payment"] = round(12 * result["request"]["duration"] * result["response"]["monthly"]["payment"], 2)
    result["response"]["total"]["interest"] = round(12 * result["request"]["duration"] * result["response"]["monthly"]["payment"] - result["request"]["loan"], 2)
    result["response"]["rate"]["payment"] = round(result["response"]["total"]["payment"] / result["request"]["loan"], 2)
    result["response"]["rate"]["interest"]  = round(result["response"]["total"]["interest"] / result["response"]["total"]["payment"], 4)
    result["response"]["monthly"]["interest"] = round(result["response"]["rate"]["interest"] * result["response"]["monthly"]["payment"], 2)
    result["response"]["monthly"]["capital"] = round(result["response"]["monthly"]["payment"] - result["response"]["monthly"]["interest"], 2)
    
    return result


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


@app.put("/users/update/{id}")
async def update(id: str, user: dict) -> dict:
    sql: str = Path(__file__).parent.joinpath("data/users/update.sql").read_text()
    user["id"] = id
    user_tuple = tuple(user.values())
    connection.cursor().execute(sql, user_tuple)
    connection.commit()

    return {"message": "User updated."}


@app.post("/users/test/{id}")
@app.put("/users/test/{id}")
async def test(id: str, user: dict) -> dict:
    print(id)
    print(user)

    return {"message": "OK"}


@app.delete("/users/delete/{id}")
async def delete(id: str) -> dict:
    sql: str = Path(__file__).parent.joinpath("data/users/delete.sql").read_text()
    connection.cursor().execute(sql, (id,))
    connection.commit()

    return {"message": "User deleted."}
