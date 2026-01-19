FROM agnohq/python:3.12

# Environment variables that actually matter
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

ARG USER=app
ARG APP_DIR=/app

# Create user
RUN groupadd -g 61000 ${USER} \
    && useradd -g 61000 -u 61000 -ms /bin/bash -d ${APP_DIR} ${USER}

WORKDIR ${APP_DIR}

# Install dependencies first (better layer caching)
COPY requirements.txt ./
RUN uv pip sync requirements.txt --system

# Copy app code
COPY --chown=${USER}:${USER} . .

USER ${USER}

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["chill"]