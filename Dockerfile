FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5001
CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app" ]
