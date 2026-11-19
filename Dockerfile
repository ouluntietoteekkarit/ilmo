FROM python:3.13-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72 AS base

FROM base AS dependencies
COPY requirements.txt /tmp/requirements.txt
RUN sed -E '/^(build|pip-review|pip-tools|pyproject_hooks|setuptools|wheel)==/d' /tmp/requirements.txt > /tmp/runtime.txt \
    && python -m venv --without-pip /opt/venv \
    && python -m pip --python /opt/venv install --no-cache-dir -r /tmp/runtime.txt \
    && python -m pip --python /opt/venv check

FROM base AS runtime
ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////var/lib/ilmo/app.db \
    ILMO_SECRET_KEY_FILE=/run/secrets/flask_secret \
    ILMO_AUTH_FILE=/run/secrets/auth_config \
    ILMO_SMTP_HOST=""

RUN groupadd --gid 10001 ilmo \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin ilmo \
    && install -d -m 0700 -o 10001 -g 10001 /var/lib/ilmo \
    && python -m pip uninstall -y pip

WORKDIR /opt/ilmo
COPY --from=dependencies /opt/venv /opt/venv
COPY app/ app/
COPY config.py wsgi.py ./
COPY routes.conf.sample routes.conf

USER 10001:10001
EXPOSE 62733
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:62733/', timeout=3).close()"]
CMD ["gunicorn", "--no-control-socket", "--bind=0.0.0.0:62733", "--workers=1", "--worker-tmp-dir=/tmp", "--umask=0o077", "--timeout=20", "wsgi:server"]
