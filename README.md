## «Продуктовый помощник»Foodgram

[![рабочий процесс](https://github.com/Timur-x/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/mikhailsoldatkin/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

Проект доступен по [адресу](http://foodgram.ddns.net/)

Документация к API доступна [здесь](http://158.160.108.93/api/docs/)

В документации описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.

### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Яндекс Облако, непрерывная интеграция, непрерывное развертывание

### Развернуть проект на удаленном сервере:

* Клонировать репозиторий:

  git clone [https://github.com/Timur-x/foodgram-project-react.git](https://github.com/Timur-x/foodgram-project-react)
* Установить на сервере Docker, Docker Compose,PostgreSQL:

  ```
  sudo apt-get update
  sudo apt install docker.io
  sudo apt install docker-compose
  sudo apt install docker-ce
  sudo apt update
  sudo apt install postgresql postgresql-contrib -y

  ```

  * #### Настройка проекта


    1. Запустите docker compose:

    ```bash
    docker-compose up -d
    ```

    2. Примените миграции:

    ```bash
    docker-compose exec backend python manage.py migrate
    ```

    3. Заполните базу начальными данными (необязательно):

    ```bash
    docker-compose exec backend python manange.py loaddata data/fixtures.json
    ```

    4. Создайте администратора:

    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```

    5. Соберите статику:

    ```bash
    docker-compose exec backend python manage.py collectstatic
    ```

    ### Импортирование с помощью скрипта своего csv файла

    ```
    	sudo docker-compose exec backend python manage.py load_ingredient
    ```

# Пользовательские роли

#### Права анонимного пользователя:

1. Создание аккаунта.
2. Просмотр: рецепты на главной, отдельные страницы рецептов, страницы пользователей.
3. Фильтрация рецептов по тегам.

#### Права авторизованного пользователя (USER):

1. Входить в систему под своим логином и паролем.
2. Выходить из системы (разлогиниваться).
3. Менять свой пароль.
4. Создавать/редактировать/удалять собственные рецепты
5. Просматривать рецепты на главной.
6. Просматривать страницы пользователей.
7. Просматривать отдельные страницы рецептов.
8. Фильтровать рецепты по тегам.
9. Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
10. Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок.
11. Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

#### Права администратора :

1. Все права авторизованного пользователя
2. Изменение пароля любого пользователя,
3. Создание/блокирование/удаление аккаунтов пользователей,
4. Редактирование/удаление любых рецептов,
5. Добавление/удаление/редактирование ингредиентов.
6. Добавление/удаление/редактирование тегов.

### Алгоритм регистрации пользователей

Для добавления нового пользователя нужно отправить POST-запрос на эндпоинт:

`POST      /api/users/									`

пример запроса:

> {
> "email": "vpupkin@yandex.ru",
> "username": "vasya.pupkin",
> "first_name": "Вася",
> "last_name": "Пупкин",
> "password": "Qwerty123"
> }

Получить авторизационный токен, отправив POST-запрос на эндпоинт:

`POST   /api/auth/token/login/							`

пример запроса:

> {
> "password": "string",
> "email": "string"
> }

---

---

Проект развернут по IP :http://foodgram.ddns.net/

Доступ в админ-панель:

пароль: Qwerty123w
Почта: 123@q.ru

---

**Автор:  [Николаев Т.А](https://github.com/Timur-x)**
