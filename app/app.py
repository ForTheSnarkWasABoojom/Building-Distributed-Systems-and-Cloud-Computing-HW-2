from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/testdb'  # Замените на ваши данные
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модели базы данных
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default="не готова")  # Статус: не готова, обработано, ошибка
    result = db.Column(db.String, nullable=True)  # Результат обработки


class NumberStatus(db.Model):
    __tablename__ = 'numbers'
    number = db.Column(db.Integer, primary_key=True)
    is_already_sent = db.Column(db.Boolean, default=False)


# Функция для очистки базы данных
def clear_database():
    with app.app_context():
        db.session.query(Transaction).delete()
        db.session.query(NumberStatus).delete()
        db.session.commit()


# Функция для обработки транзакций в фоне
def process_transactions():
    with app.app_context():  # Создаем контекст приложения
        while True:
            unprocessed_transactions = Transaction.query.filter_by(status="не готова").all()
            for transaction in unprocessed_transactions:
                number = transaction.number
                existing_number = NumberStatus.query.filter_by(number=number).first()

                # Проверка: если число уже обработано
                if existing_number and existing_number.is_already_sent:
                    transaction.status = "ошибка"
                    transaction.result = f"Ошибка: Число {number} уже обработано "
                else:
                    # Проверка: если поступившее число на единицу меньше уже обработанного числа
                    next_number = NumberStatus.query.filter_by(number=number + 1).first()
                    if next_number and next_number.is_already_sent:
                        transaction.status = "ошибка"
                        transaction.result = f"Ошибка: Поступившее число {number} на единицу меньше уже обработанного числа"
                    else:
                        # Обрабатываем впервые поступившее число
                        transaction.status = "обработано"
                        transaction.result = f"{number + 1}"

                        # Добавляем текущее число в таблицу или обновляем статус
                        if not existing_number:
                            db.session.add(NumberStatus(number=number, is_already_sent=True))
                        else:
                            existing_number.is_already_sent = True

                db.session.commit()
            time.sleep(2)  # Пауза перед следующим циклом


@app.route('/')
def home():
    return '''
    <html>
        <body>
            <h1>Транзакционная система</h1>
            <label>Введите число:</label>
            <input id="number" type="number" />
            <button onclick="sendRequest()">Отправить запрос</button>
            <button onclick="getResult()">Посмотреть результат</button>
            <script>
                function sendRequest() {
                    const number = document.getElementById("number").value;
                    if (!number) {
                        alert("Введите число");
                        return;
                    }
                    fetch('/send', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({number: parseInt(number)})})
                        .then(response => response.json())
                        .then(data => alert('ID транзакции: ' + data.transaction_id))
                        .catch(error => alert('Ошибка: ' + error));
                }
                function getResult() {
                    let transactionId = prompt("Введите ID транзакции:");
                    fetch('/result/' + transactionId)
                        .then(response => response.json())
                        .then(data => alert('Результат: ' + data.result))
                        .catch(error => alert('Ошибка: ' + error));
                }
            </script>
        </body>
    </html>
    '''


@app.route('/send', methods=['POST'])
def send_request():
    data = request.json
    number = data.get('number')

    if number is None:
        return jsonify({"error": "Введите число"}), 400

    transaction = Transaction(number=number)
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"transaction_id": transaction.id})


@app.route('/result/<int:transaction_id>', methods=['GET'])
def get_result(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Транзакция не найдена"}), 404

    return jsonify({"result": transaction.result})


if __name__ == '__main__':
    # Инициализация базы данных
    with app.app_context():
        db.create_all()
        clear_database()

    # Запуск фоновой обработки транзакций
    thread = Thread(target=process_transactions, daemon=True)
    thread.start()

    # Запуск Flask приложения
    app.run(host="0.0.0.0", port=5000)