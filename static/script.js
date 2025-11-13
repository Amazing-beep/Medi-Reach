// Medicine display and cart functionality
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Fetch and display medicines
fetch("/api/medicines")
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("medicine-container");
    if (!container) return;
    
    container.innerHTML = '';
    
    data.medicines.forEach(medicine => {
      const card = createMedicineCard(medicine);
      container.appendChild(card);
    });
    
    // Search functionality
    const searchInput = document.getElementById("medicine-search");
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const cards = container.querySelectorAll('.medicine-card');
        
        cards.forEach(card => {
          const medicineName = card.querySelector('.medicine-name').textContent.toLowerCase();
          if (medicineName.includes(searchTerm)) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        });
      });
    }
  })
  .catch(err => console.error('Error fetching medicines:', err));

// Create medicine card
function createMedicineCard(medicine) {
  const card = document.createElement('div');
  card.className = 'medicine-card';
  
  // Determine category and description
  const category = getMedicineCategory(medicine.name);
  const description = getMedicineDescription(medicine.name);
  const requiresRx = category === 'Antibiotic' ? true : false;
  const stock = Math.floor(Math.random() * 50) + 10; // Random stock for demo
  
  card.innerHTML = `
    <div class="medicine-header">
      <div class="medicine-category">${category}</div>
      ${requiresRx ? '<div class="rx-badge">Rx Required</div>' : ''}
    </div>
    <div class="medicine-name">${medicine.name}</div>
    <div class="medicine-description">${description}</div>
      <div class="medicine-footer">
      <div class="medicine-price">${formatPrice(medicine.price)}</div>
      <div class="medicine-stock">${stock} in stock</div>
    </div>
    <button class="add-to-cart-btn" onclick="addToCart(${medicine.id}, '${medicine.name.replace(/'/g, "\\'")}', ${medicine.price})">
      + Add to cart
    </button>
  `;
  
  return card;
}

// Get medicine category
function getMedicineCategory(name) {
  const nameLower = name.toLowerCase();
  if (nameLower.includes('amoxicillin') || nameLower.includes('antibiotic')) return 'Antibiotic';
  if (nameLower.includes('paracetamol') || nameLower.includes('acetaminophen')) return 'Pain Relief';
  if (nameLower.includes('omeprazole') || nameLower.includes('digestive')) return 'Digestive';
  if (nameLower.includes('cetirizine') || nameLower.includes('antihistamine')) return 'Antihistamine';
  return 'General';
}

// Get medicine description
function getMedicineDescription(name) {
  const nameLower = name.toLowerCase();
  if (nameLower.includes('amoxicillin')) return 'Amoxicillin';
  if (nameLower.includes('paracetamol')) return 'Acetaminophen';
  if (nameLower.includes('omeprazole')) return 'Omeprazole';
  if (nameLower.includes('cetirizine')) return 'Cetirizine';
  return name.split(' ')[0];
}

// Format price
function formatPrice(price) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(price);
}

// Add to cart
function addToCart(id, name, price) {
  const existingItem = cart.find(item => item.id === id);
  
  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({
      id: id,
      name: name,
      price: price,
      quantity: 1
    });
  }
  
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartBadge();
  showCartNotification(name);
}

// Update cart badge
function updateCartBadge() {
  const badge = document.getElementById('cart-badge');
  if (badge) {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    badge.textContent = totalItems;
    if (totalItems > 0) {
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }
}

// Show cart notification
function showCartNotification(medicineName) {
  const notification = document.createElement('div');
  notification.className = 'cart-notification';
  notification.textContent = `${medicineName} added to cart!`;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);
  
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 2000);
}

// Initialize cart badge on page load
document.addEventListener('DOMContentLoaded', () => {
  updateCartBadge();
});

// Tab switching for auth forms (if script.js is used in auth page)
function showTab(tab) {
  const forms = document.querySelectorAll('.auth-form');
  const tabs = document.querySelectorAll('.tab-btn');
  
  forms.forEach(form => form.classList.remove('active'));
  tabs.forEach(btn => btn.classList.remove('active'));
  
  const form = document.getElementById(tab + '-form');
  const tabBtn = event.target;
  
  if (form) form.classList.add('active');
  if (tabBtn) tabBtn.classList.add('active');
}
