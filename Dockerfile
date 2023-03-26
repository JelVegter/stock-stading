FROM python:3.11


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    curl \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip \
    && curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR /app
COPY . .

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev


EXPOSE 8080

CMD ["poetry", "run", "python", "render/app.py"]
