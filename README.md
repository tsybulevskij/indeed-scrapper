# Job parser

## Installation

Запуск контейнера командой: `docker-compose up -d`

Пересоздать(rebuild) контейнер (при изменении csv файла): `docker-compose up -d --build`

## Usage

Запуск скрапера командой: `docker exec jobparser_scrapy01 sh -c "scrapy crawl indeed"` или более простой запуск файла `./run_spider.sh` (для Windows: `sh run_spider.sh`) 

## Данные для доступа в базу
```
host -  'db'
port - '5432'
username - 'postgres'
password - 'qwerty'
database - 'jobs'
```
