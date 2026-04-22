<!DOCTYPE html>
<html>
<head>
    <title>{{product['name']}} - Python Bottle Shop</title>
    <meta charset="utf-8">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="header">
        <h1>🛍️ Python Bottle Shop</h1>
        <div class="header-buttons">
            <button class="cart-button" onclick="window.location.href='/'">
                🏠 На главную
            </button>
            <button class="cart-button" onclick="cartManager.showCart()">
                🛒 Корзина <span class="cart-count" id="cartCount">0</span>
            </button>
        </div>
    </div>

    <div class="product-detail">
        <div class="product-detail-container">
            <div class="product-detail-header">
                <div class="product-category">
                    <%
                        categories = {
                            'motherboards': 'Материнские платы',
                            'cpus': 'Процессоры',
                            'ram_rom': 'Память (RAM/ROM)',
                            'coolers': 'Охлаждение',
                            'consumables': 'Расходники',
                            'gpus': 'Видеокарты'
                        }
                    %>
                    {{categories.get(product['category'], product['category'])}}
                </div>
                <h1>{{product['name']}}</h1>
            </div>

            <div class="product-detail-content">
                <div class="product-image">
                    <img src="{{product['image_url']}}" alt="{{product['name']}}" class="product-detail-image" onerror="this.src='/static/placeholder.jpg'">
                </div>

                <div class="product-info">
                    <div class="product-description-full">
                        {{product['description']}}
                    </div>

                    <div class="product-price-large">
                        {{'{:,.0f}'.format(product['price']).replace(',', ' ')}} ₽
                    </div>

                    <div class="product-stock {{'available' if product['stock_quantity'] > 0 else 'unavailable'}}">
                        % if product['stock_quantity'] > 0:
                            ✓ В наличии: {{product['stock_quantity']}} шт.
                        % else:
                            ✗ Нет в наличии
                        % end
                    </div>

                    % if product['stock_quantity'] > 0:
                    <div class="detail-quantity-control">
                        <button class="detail-quantity-btn" onclick="decreaseQuantity()">-</button>
                        <span class="detail-quantity" id="detailQuantity">1</span>
                        <button class="detail-quantity-btn" onclick="increaseQuantity({{product['stock_quantity']}})">+</button>
                    </div>

                    <button class="detail-buy-button" onclick="addToCart({{product['id']}})">
                        🛒 Добавить в корзину
                    </button>
                    % else:
                    <button class="detail-buy-button" disabled>
                        ❌ Нет в наличии
                    </button>
                    % end

                    <a href="/" class="back-link">← Вернуться к списку товаров</a>
                </div>
            </div>
        </div>
    </div>

    % include('views/footer')

    <script>
        let currentQuantity = 1;
        const maxStock = {{product['stock_quantity']}};

        function decreaseQuantity() {
            if (currentQuantity > 1) {
                currentQuantity--;
                document.getElementById('detailQuantity').textContent = currentQuantity;
            }
        }

        function increaseQuantity(max) {
            if (currentQuantity < max) {
                currentQuantity++;
                document.getElementById('detailQuantity').textContent = currentQuantity;
            } else {
                showNotification(`Максимум ${max} шт.`, 'error');
            }
        }

        async function addToCart(productId) {
            const button = event.target;
            const originalText = button.textContent;
            button.disabled = true;
            button.textContent = '⏳ Добавление...';

            try {
                const response = await fetch('/api/cart/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        quantity: currentQuantity
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    showNotification(`✅ Товар добавлен в корзину`);
                    await updateCartCount();
                    button.textContent = '✓ Добавлено!';
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.disabled = false;
                    }, 2000);
                } else {
                    showNotification(`❌ ${result.error || 'Ошибка'}`, 'error');
                    button.textContent = originalText;
                    button.disabled = false;
                }
            } catch (error) {
                console.error('Ошибка:', error);
                showNotification('❌ Ошибка соединения', 'error');
                button.textContent = originalText;
                button.disabled = false;
            }
        }

        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification ${type === 'error' ? 'error' : ''}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 3000);
        }

        async function updateCartCount() {
            try {
                const response = await fetch('/api/cart');
                const cart = await response.json();
                let totalItems = 0;
                if (cart.items && cart.items.length > 0) {
                    totalItems = cart.items.reduce((sum, item) => sum + item.quantity, 0);
                }
                document.getElementById('cartCount').textContent = totalItems;
            } catch (error) {
                console.error('Ошибка обновления счетчика:', error);
            }
        }

        class CartManager {
            constructor() {
                this.modal = document.getElementById('cartModal');
                this.apiUrl = '/api';
            }

            showCart() {
                this.loadCart();
                this.modal.classList.add('active');
            }

            hideCart() {
                this.modal.classList.remove('active');
            }

            async loadCart() {
                try {
                    const response = await fetch(`${this.apiUrl}/cart`);
                    const cart = await response.json();
                    this.renderCart(cart);
                } catch (error) {
                    console.error('Ошибка загрузки корзины:', error);
                }
            }

            renderCart(cart) {
                const cartItems = document.getElementById('cartItems');
                const cartTotal = document.getElementById('cartTotal');

                if (!cart.items || cart.items.length === 0) {
                    cartItems.innerHTML = '<div class="empty-cart">Корзина пуста</div>';
                    cartTotal.textContent = 'Итого: 0 ₽';
                    return;
                }

                cartItems.innerHTML = cart.items.map(item => `
                    <div class="cart-item">
                        <div class="cart-item-info">
                            <div class="cart-item-name">${this.escapeHtml(item.name)}</div>
                            <div class="cart-item-details">
                                ${item.price.toLocaleString()} ₽ × ${item.quantity}
                            </div>
                        </div>
                        <div class="cart-item-price">
                            ${(item.price * item.quantity).toLocaleString()} ₽
                        </div>
                    </div>
                `).join('');

                cartTotal.textContent = `Итого: ${cart.total.toLocaleString()} ₽`;
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        }

        const cartManager = new CartManager();
        window.cartManager = cartManager;

        // Инициализация счетчика корзины
        updateCartCount();

        // Закрытие модального окна по клику вне его
        window.onclick = function(event) {
            const cartModal = document.getElementById('cartModal');
            if (event.target === cartModal) {
                cartManager.hideCart();
            }
        }
    </script>
</body>
</html>
