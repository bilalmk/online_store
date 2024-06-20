FROM python:3.12

WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . /app

CMD ["uvicorn", "users.main:app", "--host", "0.0.0.0", "--port", "8000"]
