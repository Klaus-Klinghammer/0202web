import unittest
import json
from app import app
from bottle import Bottle, request, response


class TestQuestionValidation(unittest.TestCase):
    """Тесты для валидации формы вопросов"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.app = Bottle()
        # Копируем маршруты из основного приложения
        for route in app.routes:
            self.app.route(route.rule, method=route.method, callback=route.callback)

    def test_valid_question_submission(self):
        """Тест 1: Проверка успешной отправки валидных данных"""
        from app import api_submit_question

        # Создаем имитацию запроса
        valid_data = {
            'name': 'Иван Петров',
            'email': 'ivan@example.com',
            'product_name': 'Intel Core i9-13900K',
            'question': 'Этот процессор поддерживает DDR5 память?'
        }

        # Вызываем функцию (имитируя request.json)
        result = self._call_question_api(valid_data)

        self.assertTrue(result['success'])
        self.assertIn('успешно отправлен', result['message'])

    def test_invalid_name_validation(self):
        """Тест 2: Проверка валидации имени (пустое имя)"""
        invalid_data = {
            'name': '',
            'email': 'ivan@example.com',
            'product_name': 'Intel Core i9-13900K',
            'question': 'Этот процессор поддерживает DDR5 память?'
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('name', result['errors'])
        self.assertEqual(result['errors']['name'], 'Имя обязательно для заполнения')

    def test_short_name_validation(self):
        """Тест: Имя слишком короткое"""
        invalid_data = {
            'name': 'И',
            'email': 'ivan@example.com',
            'product_name': 'Intel Core i9-13900K',
            'question': 'Этот процессор поддерживает DDR5 память?'
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('name', result['errors'])
        self.assertEqual(result['errors']['name'], 'Имя должно содержать минимум 2 символа')

    def test_long_name_validation(self):
        """Тест: Имя слишком длинное"""
        invalid_data = {
            'name': 'A' * 60,
            'email': 'ivan@example.com',
            'product_name': 'Intel Core i9-13900K',
            'question': 'Этот процессор поддерживает DDR5 память?'
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('name', result['errors'])
        self.assertEqual(result['errors']['name'], 'Имя не должно превышать 50 символов')

    def test_name_with_numbers_validation(self):
        """Тест: Имя содержит цифры"""
        invalid_data = {
            'name': 'Иван123',
            'email': 'ivan@example.com',
            'product_name': 'Intel Core i9-13900K',
            'question': 'Этот процессор поддерживает DDR5 память?'
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('name', result['errors'])
        self.assertEqual(result['errors']['name'], 'Имя должно содержать только буквы и пробелы')

    def test_invalid_email_validation(self):
        """Тест: Невалидный email (без @)"""
        invalid_data = {
            'name': 'Иван Петров',
            'email': 'ivanexample.com',
            'product_name': 'Intel Core i9-13900K',
            'question': 'Этот процессор поддерживает DDR5 память?'
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('email', result['errors'])
        self.assertIn('Введите корректный email', result['errors']['email'])

    def test_empty_email_validation(self):
        """Тест: Пустой email"""
        invalid_data = {
            'name': 'Иван Петров',
            'email': '',
            'product_name': 'Intel Core i9-13900K',
            'question': 'Этот процессор поддерживает DDR5 память?'
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('email', result['errors'])
        self.assertEqual(result['errors']['email'], 'Email обязателен для заполнения')

    def test_missing_product_name_validation(self):
        """Тест: Отсутствует название товара"""
        invalid_data = {
            'name': 'Иван Петров',
            'email': 'ivan@example.com',
            'product_name': '',
            'question': 'Этот процессор поддерживает DDR5 память?'
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('product_name', result['errors'])
        self.assertEqual(result['errors']['product_name'], 'Укажите название товара')

    def test_short_question_validation(self):
        """Тест: Вопрос слишком короткий"""
        invalid_data = {
            'name': 'Иван Петров',
            'email': 'ivan@example.com',
            'product_name': 'Intel Core i9-13900K',
            'question': 'Коротко'
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('question', result['errors'])
        self.assertEqual(result['errors']['question'], 'Вопрос должен содержать минимум 10 символов')

    def test_missing_question_validation(self):
        """Тест: Пустой вопрос"""
        invalid_data = {
            'name': 'Иван Петров',
            'email': 'ivan@example.com',
            'product_name': 'Intel Core i9-13900K',
            'question': ''
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('question', result['errors'])
        self.assertEqual(result['errors']['question'], 'Введите ваш вопрос')

    def test_multiple_validation_errors(self):
        """Тест: Несколько ошибок валидации одновременно"""
        invalid_data = {
            'name': '',
            'email': 'invalid',
            'product_name': '',
            'question': ''
        }

        result = self._call_question_api(invalid_data)

        self.assertFalse(result['success'])
        self.assertIn('name', result['errors'])
        self.assertIn('email', result['errors'])
        self.assertIn('product_name', result['errors'])
        self.assertIn('question', result['errors'])

    def _call_question_api(self, data):
        """Вспомогательный метод для вызова API с тестовыми данными"""
        from app import api_submit_question

        # Имитируем request.json
        original_json = request.json
        request.json = data

        try:
            # Вызываем функцию
            response_data = api_submit_question()
            # Парсим JSON ответ
            return json.loads(response_data.body.decode('utf-8'))
        finally:
            # Восстанавливаем оригинальный request.json
            request.json = original_json


class TestQuestionValidatorClientSide(unittest.TestCase):
    """Тесты для клиентской валидации (имитация JavaScript логики)"""

    def test_name_validator(self):
        """Тест валидатора имени"""

        # Копируем логику валидации из JavaScript
        def validate_name(name):
            if not name:
                return 'Имя обязательно для заполнения'
            if len(name) < 2:
                return 'Имя должно содержать минимум 2 символа'
            if len(name) > 50:
                return 'Имя не должно превышать 50 символов'
            # Проверка на буквы и пробелы
            if not all(c.isalpha() or c.isspace() for c in name):
                return 'Имя должно содержать только буквы и пробелы'
            return None

        # Валидные имена
        self.assertIsNone(validate_name('Иван Петров'))
        self.assertIsNone(validate_name('John Doe'))

        # Невалидные имена
        self.assertEqual(validate_name(''), 'Имя обязательно для заполнения')
        self.assertEqual(validate_name('И'), 'Имя должно содержать минимум 2 символа')
        self.assertEqual(validate_name('A' * 60), 'Имя не должно превышать 50 символов')
        self.assertEqual(validate_name('Иван123'), 'Имя должно содержать только буквы и пробелы')

    def test_email_validator(self):
        """Тест валидатора email"""

        def validate_email(email):
            if not email:
                return 'Email обязателен для заполнения'
            if '@' not in email or '.' not in email:
                return 'Введите корректный email адрес'
            if len(email) > 100:
                return 'Email не должен превышать 100 символов'
            return None

        # Валидные email
        self.assertIsNone(validate_email('user@example.com'))
        self.assertIsNone(validate_email('ivan.petrov@mail.ru'))

        # Невалидные email
        self.assertEqual(validate_email(''), 'Email обязателен для заполнения')
        self.assertEqual(validate_email('userexample.com'), 'Введите корректный email адрес')
        self.assertEqual(validate_email('user@example'), 'Введите корректный email адрес')


if __name__ == '__main__':
    unittest.main()