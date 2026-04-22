<!-- Модальное окно корзины -->
<div id="cartModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>🛒 Ваша корзина</h2>
            <button class="close-btn" onclick="cartManager.hideCart()">×</button>
        </div>
        <div id="cartItems">
            <!-- Сюда будут добавляться товары -->
        </div>
        <div id="cartTotal" class="cart-total">
            Итого: 0 ₽
        </div>
    </div>
</div>
