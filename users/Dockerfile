FROM python:3.12

WORKDIR /code

COPY pyproject.toml /code/
# COPY poetry.lock /code/
COPY shared-0.1.0-py3-none-any.whl /code/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
RUN pip install shared-0.1.0-py3-none-any.whl

COPY . /code/

# CMD ["uvicorn", "users.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
