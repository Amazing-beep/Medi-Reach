// Load cart from localStorage or default to empty array (persists between visits)
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// On page ready, render cart items and totals
document.addEventListener('DOMContentLoaded', () => {
  renderCart(); // Build cart UI
  updateCartSummary(); // Show totals
});

// Render all cart items into the cart container
function renderCart() {
  const container = document.getElementById('cart-container'); // Items wrapper
  container.innerHTML = ''; // Clear existing

  if (cart.length === 0) { // Empty state
    container.innerHTML = `
      <div class="empty-cart">
        <p>Your cart is empty 😢</p>
        <a href="/medicines" class="btn primary">Browse Medicines</a>
      </div>`;
    document.getElementById('cart-summary').style.display = 'none'; // Hide summary
    return; // Stop rendering
  }

  document.getElementById('cart-summary').style.display = 'block'; // Show summary

  // Render each item as a card row
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

    container.appendChild(card); // Append to list
  });
}

// Increase/decrease quantity of a specific item and refresh UI
function changeQuantity(id, delta) {
  const item = cart.find(i => i.id === id); // Locate item
  if (!item) return; // Guard

  item.quantity += delta; // Adjust
  if (item.quantity <= 0) { // Remove if zero
    cart = cart.filter(i => i.id !== id);
  }

  localStorage.setItem('cart', JSON.stringify(cart)); // Persist
  renderCart(); // Re-render list
  updateCartSummary(); // Update totals
  updateCartBadge(); // Update header badge
}

// Remove an item entirely from the cart
function removeFromCart(id) {
  cart = cart.filter(item => item.id !== id); // Drop item
  localStorage.setItem('cart', JSON.stringify(cart)); // Persist
  renderCart(); // Re-render
  updateCartSummary(); // Recompute totals
  updateCartBadge(); // Refresh badge
}

// Compute totals and render into summary section
function updateCartSummary() {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0); // Count items
  const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0); // Sum price

  document.getElementById('cart-total-items').textContent = totalItems; // Render count
  document.getElementById('cart-total-price').textContent = formatPrice(totalPrice) + ' RWF'; // Render price
}

// Format number with thousands separator (multiply by 1000 to display RWF)
function formatPrice(price) {
  return new Intl.NumberFormat('en-US').format(price * 1000);
}

// Navigate to order page if cart has items
document.getElementById('checkout-btn').addEventListener('click', () => {
  if (cart.length === 0) return; // Prevent empty checkout
  window.location.href = '/order'; // Go to order form
});
