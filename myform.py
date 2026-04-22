# myform.py - обработчик формы обратной связи
from bottle import post, request
import re
from datetime import datetime

@post('/home')
def my_form():
    # 7.4 Получаем данные из формы
    username = request.forms.get('USERNAME', '').strip()
    question = request.forms.get('QUEST', '').strip()
    email = request.forms.get('ADRESS', '').strip()
    
    # 7.4 Проверка заполненности полей
    if not username:
        return "Error: Please enter your name!"
    if not question:
        return "Error: Please enter your question!"
    if not email:
        return "Error: Please enter your email!"
    
    # 7.1 Паттерн (регулярное выражение) для проверки email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return "Error: Invalid email format! Example: name@domain.com"
    
    # 7.3 Получаем текущую дату
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # 7.2 Возвращаем сообщение с именем и датой
    return f"Thanks, {username}! The answer will be sent to the mail {email}. Access Date: {current_date}"