# Job parser

## Installation

Launch container by this command: `docker-compose up -d`

Rebuild container (upon changing csv file): `docker-compose up -d --build`

## Usage

Launch scrapper by this command: `docker exec jobparser_scrapy01 sh -c "scrapy crawl indeed"` or simplier file launch `./run_spider.sh` (for Windows: `sh run_spider.sh`) 

## Data to get access to the database
```
host -  'db'
port - '5432'
username - 'postgres'
password - 'qwerty'
database - 'jobs'
```
