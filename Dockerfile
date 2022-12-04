FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./requirements_web.txt /app/requirements_web.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements_web.txt

COPY ./app /app
