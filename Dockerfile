FROM python:3.9-slim-bullseye

# WORKDIR /app

RUN pip install -U pip \
    && curl -sSL https://install.python-poetry.org | python - 
ENV PATH="${PATH}:/root/.poetry/bin"

COPY common/ common/
COPY render/ render/
COPY src/ src/
COPY docker-compose.yml Dockerfile logging.ini pyproject.toml ./

RUN pip install poetry 
RUN poetry config virtualenvs.create false
RUN poetry install

EXPOSE 8080

CMD ["poetry", "run", "python", "render/app.py"]