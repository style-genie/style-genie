FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN wget https://files.pythonhosted.org/packages/c0/71/5321cd921e783288453c441fe4bbe05c0adefbf95ffa0954df3f3bac34cc/crewai-0.118.0.tar.gz

RUN pip install /app/crewai-0.118.0.tar.gz

RUN pip install -r requirements.txt

CMD ["python", "main.py"]

