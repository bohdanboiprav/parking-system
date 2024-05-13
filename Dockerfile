# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.11
FROM python:3.11.6


# Встановимо робочу директорію всередині контейнера
RUN mkdir /parking-system

WORKDIR /parking-system

COPY requirements.txt .

# Встановимо залежності всередині контейнера
RUN pip install -r requirements.txt



# Скопіюємо інші файли в робочу директорію контейнера
COPY . .

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# Установим права на выполнение для скрипта app.sh
RUN chmod +x /parking-system/docker/app.sh
