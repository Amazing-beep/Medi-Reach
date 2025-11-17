// Initialize cart state from localStorage (persisted between page loads)
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Fetch medicines from backend and render them to the medicines grid
fetch("/api/medicines") // Call REST endpoint
  .then(res => res.json()) // Parse JSON body
  .then(data => {
    const container = document.getElementById("medicine-container"); // Grid container
    if (!container) return; // If not on medicines page, skip
    
    container.innerHTML = ''; // Clear any previous content
    
    // Create and append a card for each medicine
    data.medicines.forEach(medicine => {
      const card = createMedicineCard(medicine); // Build DOM for card
      container.appendChild(card); // Add to grid
    });
    
    // Wire up live search filtering (client-side)
    const searchInput = document.getElementById("medicine-search");
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase(); // Normalize search text
        const cards = container.querySelectorAll('.medicine-card'); // All cards
        
        // Show/hide cards based on name match
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
  .catch(err => console.error('Error fetching medicines:', err)); // Log any fetch errors

// Build a single medicine card element with metadata and add-to-cart button
function createMedicineCard(medicine) {
  const card = document.createElement('div'); // Outer wrapper
  card.className = 'medicine-card'; // Styling hook
  
  // Derive display metadata from the name
  const category = getMedicineCategory(medicine.name); // Category tag
  const description = getMedicineDescription(medicine.name); // Short description
  const requiresRx = category === 'Antibiotic' ? true : false; // Antibiotics need Rx
  const stock = Math.floor(Math.random() * 50) + 10; // Demo stock value
  
  // Compose the card markup
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
  
  return card; // Return ready element
}

// Heuristic category by medicine name (demo logic)
function getMedicineCategory(name) {
  const nameLower = name.toLowerCase();
  if (nameLower.includes('amoxicillin') || nameLower.includes('antibiotic')) return 'Antibiotic';
  if (nameLower.includes('paracetamol') || nameLower.includes('acetaminophen')) return 'Pain Relief';
  if (nameLower.includes('omeprazole') || nameLower.includes('digestive')) return 'Digestive';
  if (nameLower.includes('cetirizine') || nameLower.includes('antihistamine')) return 'Antihistamine';
  return 'General';
}

// Short description by known name patterns (demo logic)
function getMedicineDescription(name) {
  const nameLower = name.toLowerCase();
  if (nameLower.includes('amoxicillin')) return 'Amoxicillin';
  if (nameLower.includes('paracetamol')) return 'Acetaminophen';
  if (nameLower.includes('omeprazole')) return 'Omeprazole';
  if (nameLower.includes('cetirizine')) return 'Cetirizine';
  return name.split(' ')[0]; // Fallback to first word
}

// Format number as localized RWF (using thousands separator, demo multiply by 1000)
function formatPrice(price) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(price);
}

// Add an item to the cart and persist to localStorage
function addToCart(id, name, price) {
  const existingItem = cart.find(item => item.id === id); // Match by id
  
  if (existingItem) {
    existingItem.quantity += 1; // Increment quantity
  } else {
    cart.push({
      id: id,
      name: name,
      price: price,
      quantity: 1
    }); // New cart entry
  }
  
  localStorage.setItem('cart', JSON.stringify(cart)); // Persist
  updateCartBadge(); // Refresh UI badge
  showCartNotification(name); // Toast feedback
}

// Compute and render the cart badge count in header
function updateCartBadge() {
  const badge = document.getElementById('cart-badge'); // Header badge element
  if (badge) {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0); // Sum quantities
    badge.textContent = totalItems; // Set count
    if (totalItems > 0) {
      badge.style.display = 'flex'; // Show when non-zero
    } else {
      badge.style.display = 'none'; // Hide when empty
    }
  }
}

// Display a temporary toast notification after adding to cart
function showCartNotification(medicineName) {
  const notification = document.createElement('div'); // Toast container
  notification.className = 'cart-notification'; // Styling hook
  notification.textContent = `${medicineName} added to cart!`; // Message
  document.body.appendChild(notification); // Attach to DOM
  
  // Animate in
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);
  
  // Animate out and remove
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

// Tab switching used by auth page when included
function showTab(tab) {
  const forms = document.querySelectorAll('.auth-form'); // All forms
  const tabs = document.querySelectorAll('.tab-btn'); // Tab buttons
  
  forms.forEach(form => form.classList.remove('active')); // Hide all
  tabs.forEach(btn => btn.classList.remove('active')); // Deactivate all
  
  const form = document.getElementById(tab + '-form'); // Target form
  const tabBtn = event.target; // Clicked tab
  
  if (form) form.classList.add('active'); // Show selected
  if (tabBtn) tabBtn.classList.add('active'); // Mark active
}
