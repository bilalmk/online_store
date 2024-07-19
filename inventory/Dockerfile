FROM python:3.12

WORKDIR /code

COPY pyproject.toml /code/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . /code/
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]