FROM python:3.13

WORKDIR /project

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/project

EXPOSE 5000

CMD ["python", "-m", "app.main"]