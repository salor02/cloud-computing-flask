# newer versions do not include precompiled wheels for some packages
FROM python:3.11-slim-bookworm

WORKDIR /app

ENV FLASK_APP=app.py
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

# the entrypoiny script performs db upgrade in order to apply possible migrations
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "wsgi:app"]