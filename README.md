How to start Application

- Clone repository
- Move into the main directory of repo `cd aestimatione`
- Setup virtual environment `python3 -m venv venv`
- Avtivate virtual env `python3 -m venv venv`
- Install poetry `pip install poetry`
- Install dependencies with poetry `poetry install --no-root`
- Start Application `python manage.py runserver`
- Run tests with `python manage.py app/apps/reconcilation/tests`

How to test

- Using the endpoint `http://127.0.0.1:8000/api/uploads/`
- Use form data inputs with fields `source`, `target` and `format`
- `source` and `target` have file input types while format accepts text input
- Check this image for an example request ![alt text](https://github.com/oldmonad/aestimatione/blob/main/Screenshot%202024-09-28%20at%2021.12.56.png?raw=true)
