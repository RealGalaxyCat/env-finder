FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY env_finder/ env_finder/

COPY pyproject.toml .
RUN pip install -e .

EXPOSE 6767

CMD ["python", "-m", "env_finder"]