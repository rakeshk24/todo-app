FROM python:3.12-slim

WORKDIR /app

# good practice
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.tx

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]