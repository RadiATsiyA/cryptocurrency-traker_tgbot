FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /cryptocurrency-traker_tgbot

# Install dependencies
COPY requirements.txt /cryptocurrency-traker_tgbot/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /cryptocurrency-traker_tgbot/

CMD ["python", "bot.py"]
