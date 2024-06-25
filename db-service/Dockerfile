FROM python:3.12

WORKDIR /code

COPY pyproject.toml /code/
#COPY poetry.lock /code/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . /code/

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
