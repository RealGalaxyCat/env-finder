FROM python:3.12-alpine

WORKDIR /app

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

RUN pip install -r requirements.txt
RUN pip install -e .

EXPOSE 6767

ENTRYPOINT ["python", "env_finder/main.py"]