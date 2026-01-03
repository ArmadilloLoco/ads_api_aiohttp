FROM python:3.11-slim

WORKDIR /aiohttp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app_aiohttp.py .

EXPOSE 8080

CMD ["python", "app_aiohttp.py"]