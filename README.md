# Описание
Это репозиторий для ачивки № 2 по предмету Построение распределенных систем и облачные вычисления
# Требования
Docker и Docker Compose для развёртывания приложения и базы данных.

# Установка и запуск
1. Клонируйте репозиторий с помощью git<br />
2. Запустите приложение<br />
#### sudo docker-compose up --build<br />
Это развернёт Flask-приложение и PostgreSQL в контейнерах.<br />

После запуска приложение будет доступно по адресу http://localhost:5000.

# Использование

Откройте http://localhost:5000 в браузере.<br />
Введите число в поле и нажмите "Отправить запрос".<br />
Приложение сохранит число и вернёт ID транзакции.<br /><br />
Чтобы проверить результат, введите ID транзакции и нажмите "Посмотреть результат".<br />
Приложение вернет результат обработки.
