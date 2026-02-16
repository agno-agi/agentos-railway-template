FROM agnohq/python:3.12

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# ---------------------------------------------------------------------------
# Create non-root user
# ---------------------------------------------------------------------------
RUN groupadd -g 61000 app \
    && useradd -g 61000 -u 61000 -ms /bin/bash app

# ---------------------------------------------------------------------------
# Application code
# ---------------------------------------------------------------------------
WORKDIR /app

COPY requirements.txt ./
RUN uv pip sync requirements.txt --system

COPY --chown=app:app . .

# ---------------------------------------------------------------------------
# Document seeding: copy sample docs so /documents can be seeded on first run
# ---------------------------------------------------------------------------
RUN mkdir -p /app/documents-seed && cp -r /app/documents/* /app/documents-seed/ 2>/dev/null || true
RUN mkdir -p /documents && chown app:app /documents

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
RUN chmod +x /app/scripts/entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["chill"]
