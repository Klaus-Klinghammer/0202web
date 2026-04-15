# models.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='shop.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Инициализация таблиц"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    stock_quantity INTEGER DEFAULT 0,
                    category TEXT,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица корзины
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    UNIQUE(user_id, product_id)
                )
            ''')

            # Проверяем, есть ли данные
            cursor.execute('SELECT COUNT(*) FROM products')
            if cursor.fetchone()[0] == 0:
                self.add_sample_products()

    def add_sample_products(self):

        sample_products = [
            # Материнские платы (motherboards) - 5 шт
            ('ASUS ROG STRIX Z790-E', 'Материнская плата для игрового ПК, socket 1700, DDR5, PCIe 5.0', 28999.99, 8, 'motherboards'),
            ('MSI MAG B660 TOMAHAWK', 'Материнская плата для рабочих станций, socket 1700, DDR4', 15999.99, 12, 'motherboards'),
            ('Gigabyte B550 AORUS PRO', 'Материнская плата для AMD Ryzen, socket AM4, PCIe 4.0', 14999.99, 10, 'motherboards'),
            ('ASRock B450M PRO4', 'Бюджетная материнская плата, socket AM4, micro-ATX', 6999.99, 15, 'motherboards'),
            ('ASUS PRIME H610M-K', 'Материнская плата для офисных ПК, socket 1700, DDR4', 5999.99, 20, 'motherboards'),

            # Процессоры (cpus) - 5 шт
            ('Intel Core i9-13900K', '24-ядерный процессор для топовых игровых ПК', 52999.99, 5, 'cpus'),
            ('Intel Core i7-13700K', '16-ядерный процессор для рабочих станций', 35999.99, 7, 'cpus'),
            ('Intel Core i5-13600K', '14-ядерный процессор для игровых ПК', 25999.99, 10, 'cpus'),
            ('AMD Ryzen 9 7950X', '16-ядерный процессор для профессиональных задач', 49999.99, 4, 'cpus'),
            ('AMD Ryzen 5 7600X', '6-ядерный процессор для сборок среднего уровня', 19999.99, 12, 'cpus'),

            # Память (ram_rom) - 6 шт
            ('Kingston FURY 32GB DDR5', '32GB (2x16) DDR5 6000MHz, RGB', 11999.99, 15, 'ram_rom'),
            ('Samsung 980 PRO 1TB', 'NVMe SSD, PCIe 4.0, скорость чтения 7000MB/s', 8999.99, 25, 'ram_rom'),
            ('Corsair Vengeance 16GB DDR4', '16GB (2x8) DDR4 3200MHz', 4999.99, 30, 'ram_rom'),
            ('WD Black SN770 500GB', 'NVMe SSD для игр, PCIe 4.0', 3999.99, 20, 'ram_rom'),
            ('G.Skill Trident Z5 64GB', '64GB (2x32) DDR5 6400MHz для профессиональных задач', 22999.99, 6, 'ram_rom'),
            ('Crucial MX500 1TB', 'SATA SSD для надежного хранения данных', 5999.99, 18, 'ram_rom'),

            # Охлаждение (coolers) - 4 шт
            ('Noctua NH-D15', 'Башенный кулер премиум-класса, тихий и эффективный', 8999.99, 8, 'coolers'),
            ('Deepcool AK620', 'Башенный кулер с отличным соотношением цена/качество', 4499.99, 15, 'coolers'),
            ('Arctic Liquid Freezer II 360', 'Система жидкостного охлаждения 360мм', 11999.99, 5, 'coolers'),
            ('Be Quiet! Dark Rock 4', 'Тихий башенный кулер для процессоров', 6999.99, 10, 'coolers'),

            # Расходники (consumables) - 5 шт
            ('Arctic MX-6', 'Термопаста, 4g, высокая теплопроводность', 499.99, 50, 'consumables'),
            ('CableMod C-Series Pro', 'Комплект кабелей для блока питания, белые', 3999.99, 12, 'consumables'),
            ('Thermal Grizzly Kryonaut', 'Премиум термопаста для разгона, 1g', 899.99, 30, 'consumables'),
            ('Комплект термопрокладок', 'Набор термопрокладок для видеокарт 1mm/1.5mm/2mm', 699.99, 25, 'consumables'),
            ('Силиконовый кабель-канал', 'Для аккуратной укладки проводов в корпусе, 2.5м', 299.99, 40, 'consumables'),

            # Видеокарты (gpus) - 5 шт
            ('NVIDIA GeForce RTX 4090', 'Топовая видеокарта для игр в 4K и AI', 159999.99, 2, 'gpus'),
            ('NVIDIA GeForce RTX 4080', 'Флагманская видеокарта для требовательных игр', 89999.99, 4, 'gpus'),
            ('AMD Radeon RX 7900 XTX', 'Топовая видеокарта от AMD для игр', 84999.99, 3, 'gpus'),
            ('NVIDIA GeForce RTX 4070 Ti', 'Видеокарта для игр в 1440p с трассировкой лучей', 64999.99, 6, 'gpus'),
            ('AMD Radeon RX 7800 XT', 'Видеокарта среднего уровня для игр', 49999.99, 8, 'gpus')
        ]


        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO products (name, description, price, stock_quantity, category)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_products)

    def get_all_products(self):
        """Получить все товары"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY id')
            columns = [description[0] for description in cursor.description]
            products = []
            for row in cursor.fetchall():
                product = dict(zip(columns, row))
                products.append(product)
            return products

    def get_product(self, product_id):
        """Получить товар по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def add_to_cart(self, user_id, product_id, quantity=1):
        """Добавить товар в корзину"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем наличие товара
            cursor.execute('SELECT stock_quantity FROM products WHERE id = ?', (product_id,))
            result = cursor.fetchone()
            if not result or result[0] < quantity:
                return {'success': False, 'error': 'Недостаточно товара'}

            # Проверяем, есть ли уже товар в корзине
            cursor.execute('''
                SELECT id, quantity FROM cart
                WHERE user_id = ? AND product_id = ?
            ''', (user_id, product_id))
            existing = cursor.fetchone()

            if existing:
                # Обновляем количество
                new_quantity = existing[1] + quantity
                cursor.execute('''
                    UPDATE cart SET quantity = ? WHERE id = ?
                ''', (new_quantity, existing[0]))
            else:
                # Добавляем новый товар
                cursor.execute('''
                    INSERT INTO cart (user_id, product_id, quantity)
                    VALUES (?, ?, ?)
                ''', (user_id, product_id, quantity))

            # Уменьшаем количество на складе
            cursor.execute('''
                UPDATE products
                SET stock_quantity = stock_quantity - ?
                WHERE id = ?
            ''', (quantity, product_id))

            conn.commit()
            return {'success': True}

    def get_cart(self, user_id):
        """Получить корзину пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.*, p.name, p.price, p.description
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
            ''', (user_id,))

            columns = [description[0] for description in cursor.description]
            items = []
            total = 0

            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                item['total_price'] = item['price'] * item['quantity']
                total += item['total_price']
                items.append(item)

            return {
                'items': items,
                'total': total
            }

    def clear_cart(self, user_id):
        """Очистить корзину"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
            conn.commit()
