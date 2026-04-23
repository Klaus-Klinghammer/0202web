# myform.py - обработчик формы обратной связи
from bottle import post, request, run
import re
from datetime import datetime
import json
import os
import pdb

# Имя JSON файла для хранения данных
JSON_FILE = 'questions_db.json'

def load_data():
    """Загружает данные из JSON файла"""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Сохраняет данные в JSON файл"""
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_question_valid(question):
    """Проверка вопроса (пункт 8): длина > 3 и не состоит из цифр"""
    if len(question) <= 3:
        return False, "Question must be longer than 3 characters"
    if question.isdigit():
        return False, "Question cannot consist only of numbers"
    return True, ""

@post('/home')
def my_form():
    # Получаем данные из формы
    username = request.forms.get('USERNAME', '').strip()
    question = request.forms.get('QUEST', '').strip()
    email = request.forms.get('ADRESS', '').strip()

    # Проверка заполненности полей
    if not username:
        return "Error: Please enter your name!"
    if not question:
        return "Error: Please enter your question!"
    if not email:
        return "Error: Please enter your email!"

    # ВАЛИДАЦИЯ ВОПРОСА (пункт 8)
    is_valid, error_msg = is_question_valid(question)
    if not is_valid:
        return f"Error: {error_msg}"

    # Проверка формата email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return "Error: Invalid email format! Example: name@domain.com"

    # Загружаем существующие данные из JSON
    data = load_data()

    # Проверка на дубликаты вопросов для этого email
    if email in data:
        # Проверяем, не задавался ли уже такой вопрос
        for entry in data[email]['questions']:
            if entry['question'].lower() == question.lower():
                return f"Error: You have already asked this question from {email}"

        # Добавляем новый вопрос в существующий список
        data[email]['questions'].append({
            'username': username,
            'question': question,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        # Новый пользователь
        data[email] = {
            'username': username,
            'questions': [{
                'username': username,
                'question': question,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }]
        }

    # Сохраняем в JSON
    save_data(data)

    # ТОЧКА ОСТАНОВА ДЛЯ ОТЛАДКИ (пункт 5-6)
    pdb.set_trace()

    # Возвращаем сообщение
    current_date = datetime.now().strftime('%Y-%m-%d')
    return f"Thanks, {username}! Your question has been saved. Answer will be sent to {email}. Date: {current_date}"

# Запуск сервера (для тестирования)
if __name__ == '__main__':
    print("Server running at http://localhost:8080")
    print("Press Ctrl+C to stop")
    run(host='localhost', port=8080, debug=True, reloader=True)
