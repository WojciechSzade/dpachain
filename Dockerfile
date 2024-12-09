ARG PYTHON_VERSION=3.12
ARG PYTHON_BUILD_VERSION=$PYTHON_VERSION-slim-bullseye

FROM python:${PYTHON_BUILD_VERSION}

ARG USER_ID
ARG GROUP_ID

ENV CONFIG=${CONFIG} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.4

RUN groupadd -g $GROUP_ID -o user && useradd -m -u $USER_ID -g user user

RUN apt-get update -y && \
    apt-get install -y && \
    apt-get install -y --no-install-recommends netcat && \
    apt-get clean && \
    pip install poetry==$POETRY_VERSION
        
COPY poetry.lock pyproject.toml ./

RUN poetry install $(test "$CONFIG" == production && echo "--only=main") --no-interaction --no-ansi

WORKDIR /opt/src

COPY ./src .


EXPOSE 8000

USER user

CMD ["poetry", "run", "fastapi", "dev", "main.py"]

        


    
