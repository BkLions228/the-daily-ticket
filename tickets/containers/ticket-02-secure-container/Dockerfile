FROM python:3.12-slim

WORKDIR /app

RUN groupadd \
    --gid 10001 \
    appuser \
    && useradd \
    --uid 10001 \
    --gid 10001 \
    --no-create-home \
    --shell /usr/sbin/nologin \
    appuser

COPY --chown=appuser:appuser app.py /app/app.py

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --start-period=2s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"]

CMD ["python", "app.py"]