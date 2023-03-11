FROM python:3.9-slim-bullseye

# WORKDIR /app

RUN pip install -U pip \
    && curl -sSL https://install.python-poetry.org | python - 
ENV PATH="${PATH}:/root/.poetry/bin"

COPY . .

RUN pip install poetry 
RUN poetry config virtualenvs.create false
RUN poetry install

CMD ["poetry", "run", "python", "render", "app.py"]