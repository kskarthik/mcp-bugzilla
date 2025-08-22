FROM docker.io/astral/uv:python3.13-alpine
COPY . /app
WORKDIR /app
RUN uv sync
ENTRYPOINT ["uv", "run", "server.py"]
