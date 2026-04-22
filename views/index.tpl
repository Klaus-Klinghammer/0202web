<!DOCTYPE html>
<html>
<head>
    <title>Магазин на Python Bottle</title>
    <meta charset="utf-8">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    % include('views/header')

    <div id="productsContainer" class="products-container">
        <div class="loading">Загрузка товаров...</div>
    </div>

    % include('views/footer')
    <h3>Ask a Question</h3>
    <form action="/home" method="post">
        <p><input type="text" size="50" name="USERNAME" placeholder="Your name"></p>
        <p><textarea rows="2" cols="50" name="QUEST" placeholder="Your question"></textarea></p>
        <p><input type="text" size="50" name="ADRESS" placeholder="Your email"></p>
        <p><input type="submit" value="Send" class="btn btn-default"></p>
    </form>
    <script>
        class FiltersManager {
            constructor() {
                this.modal = document.getElementById('filtersModal');
                this.apiUrl = '/api';
                this.filters = {
                    categories: [],
                    minPrice: null,
                    maxPrice: null,
                    inStock: false
                };
            }

            applyFilters = () => {
                const checkboxes = document.querySelectorAll('.category-filter:checked');
                this.filters.categories = Array.from(checkboxes).map(cb => cb.value);

                const minPrice = document.getElementById('minPrice');
                const maxPrice = document.getElementById('maxPrice');
                this.filters.minPrice = minPrice.value ? parseFloat(minPrice.value) : null;
                this.filters.maxPrice = maxPrice.value ? parseFloat(maxPrice.value) : null;
                this.filters.inStock = document.getElementById('inStock').checked;

                console.log('Применяем фильтры:', this.filters);
                this.sendFiltersToServer();
            }

            resetFilters = () => {
                document.querySelectorAll('.category-filter').forEach(cb => cb.checked = false);
                document.getElementById('minPrice').value = '';
                document.getElementById('maxPrice').value = '';
                document.getElementById('inStock').checked = false;

                this.filters = {
                    categories: [],
                    minPrice: null,
                    maxPrice: null,
                    inStock: false
                };

                this.sendFiltersToServer();
                this.showCustomNotification('Фильтры сброшены');
            }

            async sendFiltersToServer() {
                console.log('Отправка на сервер:', this.filters);

                try {
                    const params = new URLSearchParams();

                    if (this.filters.categories && this.filters.categories.length > 0) {
                        params.append('categories', this.filters.categories.join(','));
                    }

                    if (this.filters.minPrice) {
                        params.append('minPrice', this.filters.minPrice);
                    }

                    if (this.filters.maxPrice) {
                        params.append('maxPrice', this.filters.maxPrice);
                    }

                    if (this.filters.inStock) {
                        params.append('inStock', 'true');
                    }

                    const url = `${this.apiUrl}/products/filter?${params.toString()}`;
                    console.log('Запрос к:', url);

                    const response = await fetch(url);

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const products = await response.json();
                    console.log('Получены отфильтрованные товары:', products);

                    if (window.shopManager) {
                        shopManager.renderProducts(products);
                    }

                    this.showCustomNotification(`Найдено товаров: ${products.length}`);
                    this.hideFilters();

                } catch (error) {
                    console.error('Ошибка при фильтрации:', error);
                    this.showCustomNotification('Ошибка при фильтрации', 'error');
                }
            }

            showCustomNotification(message, type = 'success') {
                const notification = document.createElement('div');
                notification.className = `notification ${type === 'error' ? 'error' : ''}`;
                notification.textContent = message;
                document.body.appendChild(notification);
                setTimeout(() => notification.remove(), 3000);
            }

            showFilters() {
                this.modal.classList.add('active');
            }

            hideFilters() {
                this.modal.classList.remove('active');
            }
        }

        class ShopManager {
            constructor() {
                this.apiUrl = '/api';
                this.init();
            }

            async init() {
                await this.loadProducts();
                await this.updateCartCount();
            }

            async loadProducts() {
                try {
                    const response = await fetch(`${this.apiUrl}/products`);
                    const products = await response.json();
                    this.renderProducts(products);
                } catch (error) {
                    console.error('Ошибка загрузки товаров:', error);
                    this.showError('Не удалось загрузить товары');
                }
            }

            renderProducts(products) {
                const container = document.getElementById('productsContainer');
                if (!container) {
                    console.error('Контейнер productsContainer не найден!');
                    return;
                }

                container.innerHTML = '';

                if (!products || !Array.isArray(products)) {
                    container.innerHTML = '<div class="error">Ошибка: неверный формат данных</div>';
                    return;
                }

                if (products.length === 0) {
                    container.innerHTML = '<div class="empty-cart">Товары не найдены</div>';
                    return;
                }

                products.forEach(product => {
                    const card = this.createProductCard(product);
                    if (card) container.appendChild(card);
                });
            }

            createProductCard(product) {
                try {
                    if (!product) return null;

                    const card = document.createElement('div');
                    card.className = 'product-card';
                    card.dataset.productId = product.id || '0';

                    const stockQuantity = product.stock_quantity || 0;
                    const isAvailable = stockQuantity > 0;
                    const imageUrl = product.image_url || '/static/placeholder.jpg';

                    const stockStatus = isAvailable
                        ? `<span class="stock available">✓ В наличии: ${stockQuantity} шт.</span>`
                        : '<span class="stock">✗ Нет в наличии</span>';

                    const productUrl = `/product/${product.id}`;

                    card.innerHTML = `
                        <div class="product-image-container">
                            <img src="${imageUrl}" alt="${this.escapeHtml(product.name)}" class="product-image-card" onerror="this.src='/static/placeholder.jpg'">
                        </div>
                        <a href="${productUrl}" class="product-link">
                            <h3>${this.escapeHtml(product.name || 'Без названия')}</h3>
                        </a>
                        <div class="product-description">${this.escapeHtml((product.description || 'Нет описания').substring(0, 100))}${product.description && product.description.length > 100 ? '...' : ''}</div>
                        <div class="price">${(product.price || 0).toLocaleString()} ₽</div>
                        ${stockStatus}
                        <div class="quantity-control">
                            <button class="quantity-btn" onclick="window.shopManager.decreaseQuantity(this)" ${!isAvailable ? 'disabled' : ''}>-</button>
                            <span class="quantity">1</span>
                            <button class="quantity-btn" onclick="window.shopManager.increaseQuantity(this, ${stockQuantity})" ${!isAvailable ? 'disabled' : ''}>+</button>
                        </div>
                        <button class="buy-button" onclick="window.shopManager.addToCart(${product.id}, this)"
                            ${!isAvailable ? 'disabled' : ''}>
                            ${isAvailable ? 'В корзину' : 'Нет в наличии'}
                        </button>
                    `;

                    return card;
                } catch (error) {
                    console.error('Ошибка в createProductCard:', error);
                    return null;
                }
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            decreaseQuantity(btn) {
                const quantitySpan = btn.parentElement.querySelector('.quantity');
                let quantity = parseInt(quantitySpan.textContent);
                if (quantity > 1) {
                    quantitySpan.textContent = quantity - 1;
                }
            }

            increaseQuantity(btn, maxStock) {
                const quantitySpan = btn.parentElement.querySelector('.quantity');
                let quantity = parseInt(quantitySpan.textContent);

                if (quantity < maxStock) {
                    quantitySpan.textContent = quantity + 1;
                } else {
                    this.showNotification(`Максимум ${maxStock} шт.`, 'error');
                }
            }

            async addToCart(productId, button) {
                const originalText = button.textContent;
                button.disabled = true;
                button.textContent = '⏳ Добавление...';

                const card = button.closest('.product-card');
                const quantity = parseInt(card.querySelector('.quantity').textContent);

                try {
                    const response = await fetch(`${this.apiUrl}/cart/add`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            product_id: productId,
                            quantity: quantity
                        })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        this.showNotification(`✅ Товар добавлен в корзину`);
                        await this.updateCartCount();

                        const productsResponse = await fetch(`${this.apiUrl}/products`);
                        const allProducts = await productsResponse.json();

                        const updatedProduct = allProducts.find(p => p.id === productId);

                        if (updatedProduct) {
                            const newCard = this.createProductCard(updatedProduct);
                            card.parentNode.replaceChild(newCard, card);
                        }

                        button.textContent = '✓ Добавлено!';
                        setTimeout(() => {
                            if (button) button.textContent = originalText;
                        }, 2000);
                    } else {
                        this.showNotification(`❌ ${result.error || 'Ошибка'}`, 'error');
                        button.textContent = originalText;
                        button.disabled = false;
                    }
                } catch (error) {
                    console.error('Ошибка:', error);
                    this.showNotification('❌ Ошибка соединения', 'error');
                    button.textContent = originalText;
                    button.disabled = false;
                }
            }

            showNotification(message, type = 'success') {
                const notification = document.createElement('div');
                notification.className = `notification ${type === 'error' ? 'error' : ''}`;
                notification.textContent = message;
                document.body.appendChild(notification);
                setTimeout(() => notification.remove(), 3000);
            }

            showError(message) {
                const container = document.getElementById('productsContainer');
                container.innerHTML = `
                    <div style="text-align: center; width: 100%; padding: 50px;">
                        <div style="color: #ff4757; font-size: 48px; margin-bottom: 20px;">❌</div>
                        <div style="color: #666; font-size: 18px; margin-bottom: 20px;">${message}</div>
                        <button onclick="location.reload()" class="buy-button" style="width: auto; padding: 12px 30px;">
                            Попробовать снова
                        </button>
                    </div>
                `;
            }

            async updateCartCount() {
                try {
                    const response = await fetch(`${this.apiUrl}/cart`);
                    const cart = await response.json();

                    let totalItems = 0;
                    if (cart.items && cart.items.length > 0) {
                        totalItems = cart.items.reduce((sum, item) => sum + item.quantity, 0);
                    }

                    const cartCountElement = document.getElementById('cartCount');
                    if (cartCountElement) {
                        cartCountElement.textContent = totalItems;
                    }
                } catch (error) {
                    console.error('Ошибка обновления счетчика:', error);
                }
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

        // Инициализация
        const shopManager = new ShopManager();
        const cartManager = new CartManager();
        const filtersManager = new FiltersManager();

        window.shopManager = shopManager;
        window.cartManager = cartManager;
        window.filtersManager = filtersManager;

        // Закрытие модального окна по клику вне его
        window.onclick = function(event) {
            const cartModal = document.getElementById('cartModal');
            const filtersModal = document.getElementById('filtersModal');
            if (event.target === cartModal) {
                cartManager.hideCart();
            }
            if (event.target === filtersModal) {
                filtersManager.hideFilters();
            }
        }
    </script>
</body>
</html>
