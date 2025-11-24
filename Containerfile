FROM registry.suse.com/bci/python:3.13
COPY . /app
WORKDIR /app
RUN pip install uv
RUN uv sync
ENTRYPOINT ["uv", "run", "server.py"]
