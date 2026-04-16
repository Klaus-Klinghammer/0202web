from bottle import route, run, template, request, response, static_file
import json
import sqlite3
from models import Database

# Создаем экземпляр базы данных
db = Database()

# Фиксированный пользователь (для простоты демо)
USER_ID = 1


# ====================== HTML страницы ======================
@route('/')
def index():
    """Главная страница"""
    products = db.get_all_products()
    return template('views/index.html', products=products)


# ====================== Статические файлы ======================
@route('/static/<filename:path>')
def serve_static(filename):
    """Раздача статических файлов (css, js, изображения)"""
    return static_file(filename, root='./static')


# ====================== API ======================

@route('/api/products', method='GET')
def api_get_products():
    """Получить все товары"""
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

    categories = [c.strip() for c in categories_param.split(',') if c.strip()]

    products = db.get_filtered_products(
        categories=categories,
        min_price=float(min_price) if min_price else None,
        max_price=float(max_price) if max_price else None,
        in_stock=in_stock
    )

    response.content_type = 'application/json'
    return json.dumps(products, ensure_ascii=False, default=str)


@route('/api/products/<product_id:int>', method='GET')
def api_get_product(product_id):
    """Получить один товар по ID"""
    product = db.get_product(product_id)
    if product:
        response.content_type = 'application/json'
        return json.dumps(product, ensure_ascii=False, default=str)
    
    response.status = 404
    return json.dumps({'error': 'Товар не найден'})


@route('/api/cart', method='GET')
def api_get_cart():
    """Получить корзину пользователя"""
    cart = db.get_cart(USER_ID)
    response.content_type = 'application/json'
    return json.dumps(cart, ensure_ascii=False, default=str)


@route('/api/cart/add', method='POST')
def api_add_to_cart():
    """Добавить товар в корзину"""
    try:
        data = request.json or {}
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


# ====================== Запуск сервера ======================
if __name__ == '__main__':
    print("Сервер запущен на http://localhost:8080")
    print("Нажмите Ctrl+C для остановки")

    # Автоматическое закрытие соединения с БД при выходе
    import atexit
    atexit.register(db.close)   # ← если у тебя есть метод close() в Database

    run(host='localhost', port=8080, debug=True, reloader=True)