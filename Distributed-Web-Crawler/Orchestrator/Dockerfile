FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y curl
RUN pip install -r requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
