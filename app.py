# app.py
from bottle import route, run, template, request, response, static_file
import json
import sqlite3
from models import Database

# Создаем экземпляр базы данных
db = Database()

# Для простоты используем фиксированного пользователя
USER_ID = 1

# Маршруты для HTML страниц
@route('/')
def index():
    """Главная страница"""
    products = db.get_all_products()
    return template('views/index.html', products=products)
@route('/api/cart', method='GET')
def api_get_cart():
    """Получить корзину"""
    cart = db.get_cart(USER_ID)
    response.content_type = 'application/json'
    return json.dumps(cart, ensure_ascii=False, default=str)

@route('/api/cart/add', method='POST')
def api_add_to_cart():
    """Добавить товар в корзину"""
    try:
        # Получаем данные из POST запроса
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not product_id:
            response.status = 400
            return json.dumps({'error': 'Не указан ID товара'})

        # Добавляем в корзину
        result = db.add_to_cart(USER_ID, product_id, quantity)

        if result['success']:
            # Получаем обновленную корзину
            cart = db.get_cart(USER_ID)
            product = db.get_product(product_id)

            response.content_type = 'application/json'
            return json.dumps({
                'success': True,
                'message': 'Товар добавлен в корзину',
                'cart': cart,
                'product': product
            }, ensure_ascii=False, default=str)
        else:
            response.status = 400
            return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        response.status = 500
        return json.dumps({'error': str(e)})

@route('/api/cart/clear', method='POST')
def api_clear_cart():
    """Очистить корзину"""
    db.clear_cart(USER_ID)
    return json.dumps({'success': True})

@route('/static/<filename:path>')
def serve_static(filename):
    """Раздача статических файлов"""
    return static_file(filename, root='./static')

# API маршруты (роуты) для AJAX запросов
@route('/api/products', method='GET')
def api_get_products():
    """Получить все товары в JSON"""
    products = db.get_all_products()
    response.content_type = 'application/json'
    return json.dumps(products, ensure_ascii=False, default=str)


@route('/api/products/filter', method='GET')
def api_get_products_filter():
    """Расширенная фильтрация товаров"""

    # Получаем все параметры из URL
    categories_param = request.query.get('categories', '')
    min_price = request.query.get('minPrice')
    max_price = request.query.get('maxPrice')
    in_stock = request.query.get('inStock') == 'true'

    # Разбираем категории
    categories = categories_param.split(',') if categories_param else []

    # ✅ ИСПРАВЛЕНО: устанавливаем row_factory для получения словарей
    conn = db.get_connection()
    conn.row_factory = sqlite3.Row  # Теперь row можно использовать как словарь
    cursor = conn.cursor()

    # Строим динамический запрос
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    # Фильтр по категориям
    if categories and categories[0]:
        placeholders = ','.join(['?'] * len(categories))
        query += f" AND category IN ({placeholders})"
        params.extend(categories)

    # Фильтр по минимальной цене
    if min_price:
        query += " AND price >= ?"
        params.append(float(min_price))

    # Фильтр по максимальной цене
    if max_price:
        query += " AND price <= ?"
        params.append(float(max_price))

    # Фильтр по наличию
    if in_stock:
        query += " AND stock_quantity > 0"

    query += " ORDER BY id"

    cursor.execute(query, params)

    products = []
    for row in cursor.fetchall():
        # ✅ Теперь работает, потому что row - это sqlite3.Row (можно по имени)
        product = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'price': row['price'],
            'stock_quantity': row['stock_quantity'],
            'category': row['category'],
            'image_url': row['image_url']
        }
        products.append(product)

    conn.close()

    response.content_type = 'application/json'
    return json.dumps(products, ensure_ascii=False, default=str)

@route('/api/products/<product_id:int>', method='GET')
def api_get_product(product_id):
    """Получить конкретный товар"""
    product = db.get_product(product_id)
    if product:
        response.content_type = 'application/json'
        return json.dumps(product, ensure_ascii=False, default=str)
    else:
        response.status = 404
        return json.dumps({'error': 'Товар не найден'})

@route('/api/cart', method='GET')
def api_get_cart():
    """Получить корзину"""
    cart = db.get_cart(USER_ID)
    response.content_type = 'application/json'
    return json.dumps(cart, ensure_ascii=False, default=str)

@route('/api/cart/add', method='POST')
def api_add_to_cart():
    """Добавить товар в корзину"""
    try:
        # Получаем данные из POST запроса
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not product_id:
            response.status = 400
            return json.dumps({'error': 'Не указан ID товара'})

        # Добавляем в корзину
        result = db.add_to_cart(USER_ID, product_id, quantity)

        if result['success']:
            # Получаем обновленную корзину
            cart = db.get_cart(USER_ID)
            product = db.get_product(product_id)

            response.content_type = 'application/json'
            return json.dumps({
                'success': True,
                'message': 'Товар добавлен в корзину',
                'cart': cart,
                'product': product
            }, ensure_ascii=False, default=str)
        else:
            response.status = 400
            return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        response.status = 500
        return json.dumps({'error': str(e)})

@route('/api/cart/clear', method='POST')
def api_clear_cart():
    """Очистить корзину"""
    db.clear_cart(USER_ID)
    return json.dumps({'success': True})



@route('/news')
def news():
    """Страница новинок"""
    return template('views/news.html')


@route('/api/products/latest', method='GET')
def api_get_latest_products():
    """Получить последние добавленные товары (новинки)"""
    limit = request.query.get('limit', 12)
    days = request.query.get('days', 7)

    conn = db.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT * FROM products 
        WHERE created_at >= datetime('now', ?)
        ORDER BY created_at DESC, id DESC
        LIMIT ?
    """

    cursor.execute(query, (f'-{days} days', limit))

    products = []
    for row in cursor.fetchall():
        product = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'price': row['price'],
            'stock_quantity': row['stock_quantity'],
            'category': row['category'],
            'image_url': row['image_url'],
            'created_at': row['created_at']
        }
        products.append(product)

    conn.close()

    response.content_type = 'application/json'
    return json.dumps(products, ensure_ascii=False, default=str)


@route('/api/products/stats', method='GET')
def api_get_stats():
    """Получить статистику для страницы новинок"""
    conn = db.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Количество новинок за месяц
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM products 
        WHERE created_at >= datetime('now', '-30 days')
    """)
    new_count = cursor.fetchone()['count']

    # Категории с новинками
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM products 
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY category
        ORDER BY count DESC
    """)
    categories_stats = [dict(row) for row in cursor.fetchall()]

    # Средняя цена новинок
    cursor.execute("""
        SELECT AVG(price) as avg_price 
        FROM products 
        WHERE created_at >= datetime('now', '-30 days')
    """)
    avg_price = cursor.fetchone()['avg_price'] or 0

    conn.close()

    return json.dumps({
        'new_count': new_count,
        'categories_stats': categories_stats,
        'avg_price': round(avg_price, 2)
    }, ensure_ascii=False)


@route('/api/questions', method='POST')
def api_submit_question():
    """Обработка вопросов пользователей о новинках"""
    try:
        data = request.json

        # Серверная валидация
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        product_name = data.get('product_name', '').strip()
        question = data.get('question', '').strip()

        errors = {}

        # Валидация имени
        if not name:
            errors['name'] = 'Имя обязательно для заполнения'
        elif len(name) < 2:
            errors['name'] = 'Имя должно содержать минимум 2 символа'
        elif len(name) > 50:
            errors['name'] = 'Имя не должно превышать 50 символов'
        elif not name.replace(' ', '').isalpha():
            errors['name'] = 'Имя должно содержать только буквы и пробелы'

        # Валидация email
        if not email:
            errors['email'] = 'Email обязателен для заполнения'
        elif '@' not in email or '.' not in email:
            errors['email'] = 'Введите корректный email адрес'
        elif len(email) > 100:
            errors['email'] = 'Email не должен превышать 100 символов'

        # Валидация названия товара
        if not product_name:
            errors['product_name'] = 'Укажите название товара'
        elif len(product_name) < 2:
            errors['product_name'] = 'Название товара слишком короткое'
        elif len(product_name) > 100:
            errors['product_name'] = 'Название товара слишком длинное'

        # Валидация вопроса
        if not question:
            errors['question'] = 'Введите ваш вопрос'
        elif len(question) < 10:
            errors['question'] = 'Вопрос должен содержать минимум 10 символов'
        elif len(question) > 1000:
            errors['question'] = 'Вопрос не должен превышать 1000 символов'

        # Если есть ошибки, возвращаем их
        if errors:
            response.status = 400
            return json.dumps({
                'success': False,
                'errors': errors
            }, ensure_ascii=False)

        # Здесь можно сохранить вопрос в БД или отправить email
        # Для демонстрации просто логируем
        print(f"Новый вопрос от {name} ({email}) о товаре '{product_name}':")
        print(f"Вопрос: {question}")

        # Имитируем успешную отправку
        return json.dumps({
            'success': True,
            'message': 'Ваш вопрос успешно отправлен! Мы ответим вам в ближайшее время.'
        }, ensure_ascii=False)

    except Exception as e:
        response.status = 500
        return json.dumps({
            'success': False,
            'errors': {'general': f'Произошла ошибка: {str(e)}'}
        }, ensure_ascii=False)
    
# Запуск сервера
if __name__ == '__main__':
    print("Сервер запущен на http://localhost:8080")
    print("Нажмите Ctrl+C для остановки")
    run(host='localhost', port=8080, debug=True, reloader=True)
