# PyCharting
PyCharting: A video game collection, priced with PriceCharting.com

## Built With

### Backend
- [Python](https://www.python.org);
- [SQL](https://en.wikipedia.org/wiki/SQL);

### Database Engine
- [SQLite](https://www.sqlite.org/), encrypted with [SQLCipher](https://www.zetetic.net/sqlcipher/);

### Frontend
- [HTML](https://html.spec.whatwg.org/);
- [CSS](https://www.w3.org/Style/CSS/);
- [JavaScript](https://www.javascript.com/);
- [JSON](https://www.json.org/);

### Web Framework
- [FastAPI](https://fastapi.tiangolo.com);

### Web Server
- [Uvicorn](https://www.uvicorn.org/);

### Virtual Environment
- [venv](https://docs.python.org/library/venv);

### Package Management System
- [pip](https://pip.pypa.io);

### API Specification
- [OpenAPI](https://www.openapis.org/);

### Integrated Development Environment (IDE)
- [Visual Studio Code](https://code.visualstudio.com);

### AI System
- [ChatGPT](https://chat.openai.com/).

## Getting Started

### Installation
1. Install [Python](https://www.python.org/downloads/);
2. Install [Visual Studio Code](https://code.visualstudio.com/download);
3. Clone solution:
```
C:
mkdir C:\source
cd C:\source
git clone https://github.com/Simon-Charest/pycharting.git
cd C:\source\pycharting
```
4. Open solution with Visual Studio Code;
5. Create virtual environment:
```
python -m venv .venv
```
6. Activate virtual environment:
```
# Ubuntu
source .venv/bin/activate

# Windows
.venv\Scripts\Activate.ps1
```
7. Upgrade pip:
```
python -m pip install -U pip
```
8. Install requirements:
```
pip install -r requirements.txt
```
9. Configure the solution: copy `.env.example` to `.env`, which holds every setting, and set at least `DATABASE_FILE` and `DATABASE_PASSWORD`. To use the existing collection, restore your backup of the encrypted database file and its password (neither is stored in Git);
10. Run solution:
```
python .
```
11. Run tests (they use a temporary database, never the one in `.env`):
```
pytest
```
12. Browse, add, edit and delete collection entries: [PyCharting](http://localhost);
13. Consult [OpenAPI Specification](http://localhost/docs).

## Accounts
The collection page is open to all, showing only the entries tagged Selling, without what they cost or who owns them; everything else asks for an account, reached from the Sign in button. An administrator can change the collection; a collaborator can only look at it, and a buyer only at what is for sale. Manage accounts from the project folder (on the server: `DEPLOY_DIR`, with `.venv/bin/python`); passwords are typed in, never written on the command line:
```
python . add-user NAME --role administrator
python . add-user NAME --role collaborator
python . set-password NAME
python . set-role NAME collaborator
```

## Deployment
1. Set the `DEPLOY_*` settings in `.env` (see `.env.example`);
2. The first time only, once the repository is cloned on the server, copy `.env` and the database there (`DEPLOY_DIR/.env` and `DEPLOY_DIR/data/database.sqlite`): they are never in Git;
3. Deploy: commits and pushes every change, updates the server, (re)starts its service on `127.0.0.1:8000`, then brings back a copy of the production database, kept in `data/backups` and copied over the local one (`python . backup FILE` makes such a copy, even while the site runs):
```
.\bin\deploy.ps1
```

## License
- Distributed under the [MIT License](https://opensource.org/license/mit/). See [LICENSE.txt](./LICENSE.txt) for more information.

## Contact
- GitHub: [PyCharting](https://github.com/Simon-Charest/pycharting);
- Email: [Simon Charest](mailto:simoncharest@gmail.com).
