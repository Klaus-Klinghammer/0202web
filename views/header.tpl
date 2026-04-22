<div class="header">
    <h1>🛍️ Python Bottle Shop</h1>
    <div class="header-buttons">
        <button class="cart-button" onclick="cartManager.showCart()">
            🛒 Корзина <span class="cart-count" id="cartCount">0</span>
        </button>
        <button class="filters-button" onclick="filtersManager.showFilters()">
            🔍 Фильтры
        </button>
    </div>
</div>

<!-- Модальное окно фильтров -->
<div id="filtersModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>🔍 Расширенные фильтры</h2>
            <button class="close-btn" onclick="filtersManager.hideFilters()">×</button>
        </div>

        <div class="filter-section">
            <h3>📁 Категории</h3>
            <label>
                <input class="category-filter" type="checkbox" value="motherboards">
                Материнские платы
            </label>
            <label>
                <input class="category-filter" type="checkbox" value="cpus">
                Процессоры
            </label>
            <label>
                <input class="category-filter" type="checkbox" value="ram_rom">
                Память (RAM/ROM)
            </label>
            <label>
                <input class="category-filter" type="checkbox" value="coolers">
                Охлаждение
            </label>
            <label>
                <input class="category-filter" type="checkbox" value="consumables">
                Расходники
            </label>
            <label>
                <input class="category-filter" type="checkbox" value="gpus">
                Видеокарты
            </label>
        </div>

        <div class="filter-section">
            <h3>💰 Ценовой диапазон</h3>
            <div class="price-range">
                <input type="number" id="minPrice" placeholder="От" class="price-input">
                <span>-</span>
                <input type="number" id="maxPrice" placeholder="До" class="price-input">
            </div>
        </div>

        <div class="filter-section">
            <h3>📦 Наличие</h3>
            <label>
                <input type="checkbox" id="inStock">
                Только товары в наличии
            </label>
        </div>

        <div class="filter-buttons">
            <button class="apply-filters-btn" onclick="filtersManager.applyFilters()">
                Применить фильтры
            </button>
            <button class="reset-filters-btn" onclick="filtersManager.resetFilters()">
                Сбросить все
            </button>
        </div>
    </div>
</div>
