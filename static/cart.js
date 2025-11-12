// =======================
// CART PAGE FUNCTIONALITY
// =======================
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Initialize cart display
document.addEventListener('DOMContentLoaded', () => {
  renderCart();
  updateCartSummary();
});

// Render cart items
function renderCart() {
  const container = document.getElementById('cart-container');
  container.innerHTML = '';

  if (cart.length === 0) {
    container.innerHTML = `
      <div class="empty-cart">
        <p>Your cart is empty 😢</p>
        <a href="/medicines" class="btn primary">Browse Medicines</a>
      </div>`;
    document.getElementById('cart-summary').style.display = 'none';
    return;
  }

  document.getElementById('cart-summary').style.display = 'block';

  cart.forEach(item => {
    const card = document.createElement('div');
    card.className = 'cart-item';

    card.innerHTML = `
      <div class="item-info">
        <h3>${item.name}</h3>
        <p class="price">${formatPrice(item.price)} RWF each</p>
      </div>
      <div class="item-controls">
        <button class="qty-btn" onclick="changeQuantity(${item.id}, -1)">−</button>
        <span class="qty">${item.quantity}</span>
        <button class="qty-btn" onclick="changeQuantity(${item.id}, 1)">+</button>
        <span class="item-total">${formatPrice(item.price * item.quantity)} RWF</span>
        <button class="remove-btn" onclick="removeFromCart(${item.id})">🗑️</button>
      </div>
    `;

    container.appendChild(card);
  });
}

// Update quantity
function changeQuantity(id, delta) {
  const item = cart.find(i => i.id === id);
  if (!item) return;

  item.quantity += delta;
  if (item.quantity <= 0) {
    cart = cart.filter(i => i.id !== id);
  }

  localStorage.setItem('cart', JSON.stringify(cart));
  renderCart();
  updateCartSummary();
  updateCartBadge();
}

// Remove item completely
function removeFromCart(id) {
  cart = cart.filter(item => item.id !== id);
  localStorage.setItem('cart', JSON.stringify(cart));
  renderCart();
  updateCartSummary();
  updateCartBadge();
}

// Update summary totals
function updateCartSummary() {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  document.getElementById('cart-total-items').textContent = totalItems;
  document.getElementById('cart-total-price').textContent = formatPrice(totalPrice) + ' RWF';
}

// Format RWF currency
function formatPrice(price) {
  return new Intl.NumberFormat('en-US').format(price * 1000);
}

// Proceed to checkout
document.getElementById('checkout-btn').addEventListener('click', () => {
  if (cart.length === 0) return;
  window.location.href = '/order';
});
