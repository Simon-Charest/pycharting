# APy
A minimalist Python backend application utilizing a FastAPI framework, with data storage managed by a SQLite database.

## Built With
- [Python](https://www.python.org);
- [Visual Studio Code](https://code.visualstudio.com);
- [venv](https://docs.python.org/library/venv);
- [pip](https://pip.pypa.io);
- [FastAPI](https://fastapi.tiangolo.com);
- [Uvicorn](https://www.uvicorn.org/);
- [SQLite](https://www.sqlite.org/);
- [Insomnia](https://insomnia.rest/products/insomnia).

## Getting Started

### Installation
1. Install [Python](https://www.python.org/downloads/);
2. Install [Visual Studio Code](https://code.visualstudio.com/download);
3. Clone solution:
```
C:
mkdir C:\source
cd C:\source
git clone https://github.com/Simon-Charest/apy.git
cd C:\source\apy
```
4. Open solution with Visual Studio Code;
5. Create virtual environment:
```
python -m venv .venv
```
6. Activate virtual environment:
```
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
9. Initialize database
```
python -m apy.data.db
```
10. Run solution:
```
uvicorn apy.main:app --reload
```
11. Run tests:
```
pytest
```
12. Download and install [Insomnia](https://insomnia.rest/products/insomnia) (or any other API client).

## License
- Distributed under the [MIT License](https://opensource.org/license/mit/). See [LICENSE.txt](./LICENSE.txt) for more information.

## Contact
- GitHub: [APy](https://github.com/Simon-Charest/apy);
- Email: [Simon Charest](mailto:simoncharest@gmail.com).

## Acknowledgments
- [ChatGPT](https://chat.openai.com/).
