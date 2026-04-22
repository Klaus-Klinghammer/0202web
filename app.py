# app.py
from bottle import route, run, template, request, response, static_file
import json
import sqlite3
from models import Database
import myform

# Создаем экземпляр базы данных
db = Database()

# Для простоты используем фиксированного пользователя
USER_ID = 1

# Маршруты для HTML страниц
@route('/')
def index():
    """Главная страница"""
    products = db.get_all_products()
    return template('views/index', products=products)

@route('/product/<product_id:int>')
def product_detail(product_id):
    """Страница товара"""
    product = db.get_product(product_id)
    if not product:
        return template('views/404', message="Товар не найден")
    return template('views/product_detail', product=product)

@route('/static/<filepath:path>')
def serve_static(filepath):
    """Раздача статических файлов"""
    return static_file(filepath, root='./static')

# API маршруты для AJAX запросов
@route('/api/products', method='GET')
def api_get_products():
    """Получить все товары в JSON"""
    products = db.get_all_products()
    response.content_type = 'application/json'
    return json.dumps(products, ensure_ascii=False, default=str)

@route('/api/products/filter', method='GET')
def api_get_products_filter():
    """Расширенная фильтрация товаров"""
    categories_param = request.query.get('categories', '')
    min_price = request.query.get('minPrice')
    max_price = request.query.get('maxPrice')
    in_stock = request.query.get('inStock') == 'true'

    categories = categories_param.split(',') if categories_param else []

    conn = db.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if categories and categories[0]:
        placeholders = ','.join(['?'] * len(categories))
        query += f" AND category IN ({placeholders})"
        params.extend(categories)

    if min_price:
        query += " AND price >= ?"
        params.append(float(min_price))

    if max_price:
        query += " AND price <= ?"
        params.append(float(max_price))

    if in_stock:
        query += " AND stock_quantity > 0"

    query += " ORDER BY id"

    cursor.execute(query, params)

    products = []
    for row in cursor.fetchall():
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
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not product_id:
            response.status = 400
            return json.dumps({'error': 'Не указан ID товара'})

        result = db.add_to_cart(USER_ID, product_id, quantity)

        if result['success']:
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

# Запуск сервера
if __name__ == '__main__':
    print("Сервер запущен на http://localhost:8080")
    print("Нажмите Ctrl+C для остановки")
    run(host='localhost', debug=True, reloader=True)
