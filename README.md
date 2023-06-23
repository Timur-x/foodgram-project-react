## «Продуктовый помощник»Foodgram

[![рабочий процесс](https://github.com/Timur-x/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/mikhailsoldatkin/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

Проект доступен по [адресу](https://158.160.108.93/)

Документация к API доступна [здесь](https://158.160.108.93/api/docs/)

В документации описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.

### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Яндекс Облако, непрерывная интеграция, непрерывное развертывание

### Развернуть проект на удаленном сервере:

* Клонировать репозиторий:

  git clone https://github.com/Timur-x/foodgram-project-react.git
* Установить на сервере Docker, Docker Compose,PostgreSQL,NGNX:

  ```
  sudo apt-get update
  sudo apt install docker.io
  sudo apt install docker-compose
  sudo apt install docker-ce
  sudo apt update
  sudo apt install postgresql postgresql-contrib -y
  sudo apt install nginx -y 

  ```
* Разрешите запросы по протоколам HTTP, HTTPS и SSH, выполнив команды:

  `sudo ufw allow 'Nginx Full'`
  `sudo ufw allow OpenSSH`

  включите файрвол:

  `sudo ufw enable`

  Проверьте внесённые изменения:`sudo ufw status`
  Запустите nginx:
  `sudo systemctl start nginx`
  Перезагрузит сервер:
  `sudo systemctl reload nginx`
